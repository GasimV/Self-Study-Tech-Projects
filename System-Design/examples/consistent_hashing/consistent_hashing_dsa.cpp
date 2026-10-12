// Educational hash-ring core: placement only, not a distributed storage service.
// Independently written; not copied from or compatible with Envoy or bRPC.
#include <cstdint>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <stdexcept>
#include <string>
#include <utility>

namespace consistent_hashing_dsa {

// Fixed non-cryptographic teaching hash: byte accumulation, then bit mixing.
// Unsigned 64-bit overflow is intentional; identical bytes give identical hashes.
std::uint64_t Hash(const std::string& text) {
    std::uint64_t h = 14695981039346656037ULL;
    for (unsigned char byte : text) {
        h ^= byte;
        h *= 1099511628211ULL;
    }
    h = (h ^ (h >> 30)) * 0xbf58476d1ce4e5b9ULL;
    h = (h ^ (h >> 27)) * 0x94d049bb133111ebULL;
    return h ^ (h >> 31);
}

// Token IDs break ties when two positions hash to the same number.
using Token = std::pair<std::uint64_t, std::string>;
struct Ring {
    const std::size_t virtualNodes;
    std::map<Token, std::string> tokens; // Sorted (position, token ID) -> server.
    std::set<std::string> servers;       // Reject duplicate physical membership.

    explicit Ring(std::size_t count) : virtualNodes(count) {
        if (count == 0) throw std::invalid_argument("Use at least one token per server");
    }
};

bool AddServer(Ring& ring, const std::string& server) {
    if (server.empty()) throw std::invalid_argument("Server ID must not be empty");
    if (!ring.servers.insert(server).second) return false;
    for (std::size_t i = 0; i < ring.virtualNodes; ++i) {
        const std::string id = server + "#" + std::to_string(i);
        ring.tokens.emplace(Token{Hash(id), id}, server);
    }
    return true;
}

bool RemoveServer(Ring& ring, const std::string& server) {
    if (ring.servers.erase(server) == 0) return false;
    for (std::size_t i = 0; i < ring.virtualNodes; ++i) {
        const std::string id = server + "#" + std::to_string(i);
        ring.tokens.erase(Token{Hash(id), id});
    }
    return true;
}

std::optional<std::string> GetServer(const Ring& ring, const std::string& key) {
    if (ring.tokens.empty()) return std::nullopt;
    auto next = ring.tokens.lower_bound(Token{Hash(key), ""});
    if (next == ring.tokens.end()) next = ring.tokens.begin(); // Wrap clockwise.
    return next->second;
}

} // namespace consistent_hashing_dsa

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: consistent_hashing_dsa.exe\n";
        return 1;
    }
    using namespace consistent_hashing_dsa;
    Ring ring(4); // Four virtual nodes for each physical server.
    for (const auto* server : {"server0", "server1", "server2", "server3"}) {
        AddServer(ring, server);
    }
    std::map<std::string, std::string> previous;
    const auto show = [&](const char* title) {
        std::cout << title << " (" << ring.servers.size() << " servers, "
                  << ring.tokens.size() << " tokens)\n";
        for (const auto* key : {"customer1", "customer2", "customer4", "customer6", "customer12"}) {
            const auto owner = GetServer(ring, key);
            std::cout << "  " << key << " -> " << *owner;
            const auto old = previous.find(key);
            if (old != previous.end() && old->second != *owner) {
                std::cout << " (moved from " << old->second << ")";
            }
            std::cout << '\n';
            previous[key] = *owner;
        }
    };
    show("INITIAL");
    AddServer(ring, "server4");
    std::cout << '\n';
    show("AFTER ADD server4");
    RemoveServer(ring, "server1");
    std::cout << '\n';
    show("AFTER REMOVE server1");
    return 0;
}
