// Educational, nonnegative-update Count-Min Sketch: approximate counts only.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <limits>
#include <map>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace count_min_sketch_dsa {
using Count = std::uint64_t;

// Seeded, non-cryptographic teaching hash; no key-specific lookup table.
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

struct Sketch {
    const std::size_t width;
    const std::vector<std::uint64_t> seeds; // One fixed hash seed per row.
    std::vector<std::vector<Count>> counters;
    Count total = 0; // Total update weight, not a count of distinct keys.

    Sketch(std::size_t w, std::vector<std::uint64_t> hashSeeds)
        : width(w), seeds(std::move(hashSeeds)),
          counters(seeds.size(), std::vector<Count>(w, 0)) {
        if (w == 0 || seeds.empty()) throw std::invalid_argument("Use positive width and depth");
    }
};

void Update(Sketch& sketch, const std::string& key, std::int64_t increment = 1) {
    if (increment < 0) throw std::invalid_argument("Negative updates are not supported");
    const auto weight = static_cast<Count>(increment);
    if (weight == 0) return;
    if (weight > std::numeric_limits<Count>::max() - sketch.total) {
        throw std::overflow_error("Total update weight would overflow");
    }
    // Every counter is <= total for intact nonnegative-update state, so this
    // total-overflow check also protects every cell before any change is made.
    for (std::size_t row = 0; row < sketch.seeds.size(); ++row) {
        const auto col = static_cast<std::size_t>(Hash(key, sketch.seeds[row]) % sketch.width);
        sketch.counters[row][col] += weight;
    }
    sketch.total += weight;
}

Count Estimate(const Sketch& sketch, const std::string& key) {
    Count result = std::numeric_limits<Count>::max();
    for (std::size_t row = 0; row < sketch.seeds.size(); ++row) {
        const auto col = static_cast<std::size_t>(Hash(key, sketch.seeds[row]) % sketch.width);
        result = std::min(result, sketch.counters[row][col]);
    }
    return result; // Upper bound, not necessarily the exact frequency.
}
} // namespace count_min_sketch_dsa

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: count_min_sketch_dsa.exe\n";
        return 1;
    }
    using namespace count_min_sketch_dsa;
    Sketch sketch(10, {6628, 589, 14217, 23745, 213});
    std::map<std::string, Count> exact; // Demo ground truth only, not sketch state.
    const auto show = [&](const std::string& title) {
        std::cout << '\n' << title << "\ncol:";
        for (std::size_t col = 0; col < sketch.width; ++col) std::cout << ' ' << col;
        std::cout << '\n';
        for (std::size_t row = 0; row < sketch.seeds.size(); ++row) {
            std::cout << 'h' << row + 1 << ": ";
            for (std::size_t col = 0; col < sketch.width; ++col) {
                if (col != 0) std::cout << ' ';
                std::cout << sketch.counters[row][col];
            }
            std::cout << '\n';
        }
    };
    const auto query = [&]() {
        for (const auto* key : {"A", "B", "C", "D"}) {
            std::cout << key << ": estimate " << Estimate(sketch, key)
                      << ", exact " << exact[key] << '\n';
        }
    };
    std::cout << "w = 10 counters per row, d = 5 hash rows\n";
    show("INITIAL");
    std::string prefix;
    for (char letter : std::string("AABD")) {
        const std::string key(1, letter);
        Update(sketch, key);
        ++exact[key];
        if (!prefix.empty()) prefix += ", ";
        prefix += key;
        show("AFTER " + prefix);
    }
    query();
    for (char letter : std::string("BAADBB")) {
        const std::string key(1, letter);
        Update(sketch, key);
        ++exact[key];
    }
    show("FINAL (10 events)");
    query();
    Sketch collision(1, {11, 22}); // All keys collide in each one-column row.
    Update(collision, "X", 3);
    Update(collision, "Y", 2);
    std::cout << "\nFORCED COLLISIONS (w = 1, d = 2)\n"
              << "X: estimate " << Estimate(collision, "X") << ", exact 3\n"
              << "Z: estimate " << Estimate(collision, "Z") << ", exact 0 (never inserted)\n";
    return 0;
}
