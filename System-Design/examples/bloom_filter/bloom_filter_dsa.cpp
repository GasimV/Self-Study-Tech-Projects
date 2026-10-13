// Educational, insertion-only Bloom filter. No deletion or distributed updates.
#include <cstdint>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace bloom_filter_dsa {

// Fixed non-cryptographic teaching hash; a seed selects each hash function.
std::uint64_t Hash(const std::string& text, std::uint64_t seed) {
    std::uint64_t h = 14695981039346656037ULL ^ seed;
    for (unsigned char byte : text) {
        h ^= byte;
        h *= 1099511628211ULL;
    }
    h = (h ^ (h >> 30)) * 0xbf58476d1ce4e5b9ULL;
    h = (h ^ (h >> 27)) * 0x94d049bb133111ebULL;
    return h ^ (h >> 31);
}

struct BloomFilter {
    const std::size_t bitCount;
    const std::vector<std::uint64_t> seeds; // Fixed configuration for all operations.
    std::vector<std::uint64_t> words;      // Explicitly packed: 64 bits per word.

    BloomFilter(std::size_t m, std::vector<std::uint64_t> hashSeeds)
        : bitCount(m), seeds(std::move(hashSeeds)),
          words(m / 64 + (m % 64 != 0), 0) {
        if (m == 0 || seeds.empty()) {
            throw std::invalid_argument("Use positive bit count and at least one hash seed");
        }
    }
};

void Insert(BloomFilter& filter, const std::string& key) {
    for (auto seed : filter.seeds) {
        const auto p = static_cast<std::size_t>(Hash(key, seed) % filter.bitCount);
        filter.words[p / 64] |= std::uint64_t{1} << (p % 64);
    }
}

bool MayContain(const BloomFilter& filter, const std::string& key) {
    for (auto seed : filter.seeds) {
        const auto p = static_cast<std::size_t>(Hash(key, seed) % filter.bitCount);
        if ((filter.words[p / 64] & (std::uint64_t{1} << (p % 64))) == 0) {
            return false; // Definitely absent from the set represented by this filter.
        }
    }
    return true; // Possibly present, NOT proof of membership.
}

} // namespace bloom_filter_dsa

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: bloom_filter_dsa.exe\n";
        return 1;
    }
    using namespace bloom_filter_dsa;
    // Seeds chosen to reproduce the notes' positions; hashing accepts any string.
    BloomFilter filter(10, {100824, 12406});
    std::set<std::string> exact; // Demo ground truth only; not part of the filter.
    const auto showBits = [&]() {
        std::cout << '[';
        for (std::size_t p = 0; p < filter.bitCount; ++p) {
            if (p != 0) std::cout << ", ";
            std::cout << ((filter.words[p / 64] >> (p % 64)) & 1);
        }
        std::cout << "]\n";
    };
    const auto showPositions = [&](const std::string& key) {
        std::cout << " (" << Hash(key, filter.seeds[0]) % filter.bitCount
                  << ", " << Hash(key, filter.seeds[1]) % filter.bitCount << ")";
    };
    std::cout << "m = 10 bits, k = 2 hash functions\nINITIAL: ";
    showBits();
    for (const auto* key : {"john", "dave", "peter"}) {
        Insert(filter, key);
        exact.insert(key);
        std::cout << "INSERT " << key;
        showPositions(key);
        std::cout << ": ";
        showBits();
    }
    std::cout << '\n';
    for (const auto* key : {"donald", "sarah", "john"}) {
        const bool possible = MayContain(filter, key);
        const bool present = exact.count(key) != 0;
        std::cout << "QUERY " << key;
        showPositions(key);
        std::cout << ": " << (possible ? "POSSIBLY PRESENT" : "DEFINITELY ABSENT")
                  << "; exact set: " << (present ? "present" : "absent");
        if (possible && !present) std::cout << " (false positive)";
        std::cout << '\n';
    }
    return 0;
}
