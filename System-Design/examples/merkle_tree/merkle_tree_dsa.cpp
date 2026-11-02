// Educational Merkle tree. FNV-1a is NOT a cryptographic integrity check.
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

namespace merkle_tree_dsa {
using Hash = std::uint64_t;
constexpr Hash offset = 14695981039346656037ULL;

Hash HashByte(Hash hash, unsigned char byte) {
    return (hash ^ byte) * 1099511628211ULL; // Defined unsigned wraparound.
}

Hash HashLeaf(std::string_view block) {
    Hash hash = HashByte(offset, 0); // Prefix 0: real block, including empty strings.
    for (unsigned char byte : block) hash = HashByte(hash, byte);
    return hash;
}

Hash HashParent(Hash left, Hash right) {
    Hash hash = HashByte(offset, 1); // Prefix 1: two fixed-width child hashes.
    for (Hash child : {left, right}) {
        for (int shift = 56; shift >= 0; shift -= 8) {
            hash = HashByte(hash, static_cast<unsigned char>(child >> shift));
        }
    }
    return hash; // Children encoded as 8-byte big-endian integers, left first.
}

struct MerkleTree {
    std::size_t count;       // Actual blocks; caller keeps their payloads.
    std::size_t base;        // Power-of-two leaf capacity, at least one.
    std::vector<Hash> nodes; // Root at 1; leaves start at base; index 0 unused.
};

MerkleTree Build(const std::vector<std::string>& blocks) {
    std::size_t base = 1;
    const auto maxNodes = std::vector<Hash>().max_size();
    while (base < blocks.size()) {
        if (base > maxNodes / 2) throw std::length_error("Tree is too large");
        base *= 2;
    }
    if (base > maxNodes / 2) throw std::length_error("Tree is too large");
    MerkleTree tree{blocks.size(), base,
                    std::vector<Hash>(2 * base, HashByte(offset, 2))};
    // Prefix 2 marks padding, so it differs from a real empty block.
    for (std::size_t i = 0; i < blocks.size(); ++i) {
        tree.nodes[base + i] = HashLeaf(blocks[i]);
    }
    for (std::size_t i = base - 1; i > 0; --i) {
        tree.nodes[i] = HashParent(tree.nodes[2 * i], tree.nodes[2 * i + 1]);
    }
    return tree; // Empty input has one padding leaf as its root.
}

void Update(MerkleTree& tree, std::size_t index, std::string_view block) {
    if (index >= tree.count) throw std::out_of_range("Block index out of range");
    std::size_t node = tree.base + index;
    tree.nodes[node] = HashLeaf(block);
    while (node > 1) {
        node /= 2;
        tree.nodes[node] = HashParent(tree.nodes[2 * node], tree.nodes[2 * node + 1]);
    }
}

void Compare(const MerkleTree& a, const MerkleTree& b, std::size_t node,
             std::vector<std::size_t>& differences) {
    if (a.nodes[node] == b.nodes[node]) return; // Skip a matching subtree.
    if (node >= a.base) {
        const auto index = node - a.base;
        if (index < a.count) differences.push_back(index);
        return;
    }
    Compare(a, b, 2 * node, differences);
    Compare(a, b, 2 * node + 1, differences);
}

std::vector<std::size_t> FindDifferences(const MerkleTree& a, const MerkleTree& b) {
    if (a.count != b.count) throw std::invalid_argument("Block counts must match");
    std::vector<std::size_t> differences;
    Compare(a, b, 1, differences);
    return differences; // Ascending indexes because the left child is visited first.
}
} // namespace merkle_tree_dsa

void PrintRoot(const char* replica, const merkle_tree_dsa::MerkleTree& tree) {
    std::cout << "  " << replica << " root: " << std::hex << std::setw(16)
              << std::setfill('0') << tree.nodes[1] << std::dec << std::setfill(' ')
              << '\n';
}

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: merkle_tree_dsa.exe\n";
        return 1;
    }
    using namespace merkle_tree_dsa;
    const std::vector<std::string> source{"Alice", "Bob", "Carol", "Dave"};
    auto replica = source;
    const auto a = Build(source);
    auto b = Build(replica);
    std::cout << "HASH: 64-bit FNV-1a (teaching only; not cryptographic)\n"
              << "BLOCKS: 1=Alice, 2=Bob, 3=Carol, 4=Dave\nINITIAL\n";
    PrintRoot("A", a);
    PrintRoot("B", b);
    std::cout << "  Roots match: " << (a.nodes[1] == b.nodes[1] ? "yes" : "no")
              << "\n\nCHANGE B: block 3 (index 2), Carol -> Carl\n";
    replica[2] = "Carl";
    Update(b, 2, replica[2]);
    PrintRoot("A", a);
    PrintRoot("B", b);
    const auto differences = FindDifferences(a, b);
    std::cout << "DIFFERENCES: " << differences.size() << '\n';
    for (auto index : differences) {
        std::cout << "  Block " << index + 1 << " (index " << index << "): A=\""
                  << source[index] << "\", B=\"" << replica[index] << "\"\n";
    }
    std::cout << "REPAIR POLICY: trust A; copy only differing blocks to B\n";
    for (auto index : differences) {
        replica[index] = source[index];
        Update(b, index, replica[index]);
        std::cout << "  Copy block " << index + 1 << ": " << replica[index] << '\n';
    }
    std::cout << "AFTER REPAIR\n";
    PrintRoot("A", a);
    PrintRoot("B", b);
    const bool equal = a.nodes[1] == b.nodes[1];
    std::cout << "  Roots match: " << (equal ? "yes" : "no") << '\n';
    return equal ? 0 : 1;
}
