// Educational dense HyperLogLog: 64-bit hashes and small-range correction.
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>

namespace hyperloglog_dsa {
std::uint64_t Hash(const std::string& key, std::uint64_t seed) {
    std::uint64_t h = 14695981039346656037ULL ^ seed;
    for (unsigned char byte : key) {
        h ^= byte;
        h *= 1099511628211ULL;
    }
    h = (h ^ (h >> 30)) * 0xbf58476d1ce4e5b9ULL;
    h = (h ^ (h >> 27)) * 0x94d049bb133111ebULL;
    return h ^ (h >> 31); // Deterministic, non-cryptographic teaching hash.
}

std::size_t RegisterCount(int precision) {
    if (precision < 4 || precision > 18) {
        throw std::invalid_argument("Precision must be between 4 and 18");
    }
    return std::size_t{1} << precision; // Validate BEFORE shifting/allocating.
}

struct HyperLogLog {
    const int precision;
    const std::uint64_t seed;
    std::vector<std::uint8_t> registers;
    explicit HyperLogLog(int p, std::uint64_t hashSeed = 42)
        : precision(p), seed(hashSeed), registers(RegisterCount(p), 0) {}
};

// Position of the first 1 in the remaining 64-p bits, starting at 1.
// The all-zero remainder has rank (64-p)+1; no undefined zero-bit intrinsic.
std::uint8_t Rank(std::uint64_t hash, int precision) {
    RegisterCount(precision);
    std::uint64_t remaining = hash << precision;
    int rank = 1;
    while (rank <= 64 - precision && (remaining & (std::uint64_t{1} << 63)) == 0) {
        ++rank;
        remaining <<= 1;
    }
    return static_cast<std::uint8_t>(rank);
}

void Insert(HyperLogLog& sketch, const std::string& key) {
    const auto hash = Hash(key, sketch.seed);
    const auto bucket = static_cast<std::size_t>(hash >> (64 - sketch.precision));
    sketch.registers[bucket] = std::max(sketch.registers[bucket], Rank(hash, sketch.precision));
}

double Estimate(const HyperLogLog& sketch) {
    const double m = static_cast<double>(sketch.registers.size());
    const double alpha = m == 16 ? 0.673 : m == 32 ? 0.697 : m == 64 ? 0.709
                                              : 0.7213 / (1.0 + 1.079 / m);
    double sum = 0;
    std::size_t empty = 0;
    for (auto rank : sketch.registers) {
        sum += std::ldexp(1.0, -static_cast<int>(rank)); // 2^(-rank).
        if (rank == 0) ++empty;
    }
    const double raw = alpha * m * m / sum;
    if (raw <= 2.5 * m && empty != 0) {
        return m * std::log(m / static_cast<double>(empty)); // Linear counting.
    }
    return raw; // No large-range or HLL++ bias correction in this example.
}

void Merge(HyperLogLog& destination, const HyperLogLog& source) {
    if (destination.precision != source.precision || destination.seed != source.seed) {
        throw std::invalid_argument("Merge requires matching precision and hash seed");
    }
    for (std::size_t i = 0; i < destination.registers.size(); ++i) {
        destination.registers[i] = std::max(destination.registers[i], source.registers[i]);
    }
}
} // namespace hyperloglog_dsa

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: hyperloglog_dsa.exe\n";
        return 1;
    }
    using namespace hyperloglog_dsa;
    HyperLogLog visitors(4); // 16 registers make the walkthrough easy to inspect.
    std::set<std::string> exact; // Demonstration ground truth, not HLL state.
    std::cout << std::fixed << std::setprecision(2)
              << "p = 4, m = 16 registers, hash seed = 42\n"
              << "INITIAL: estimate " << Estimate(visitors) << '\n';
    for (const auto* key : {"John_1275", "David.raymond23", "Sarah1978", "John",
                            "John_1275", "Sarah1978"}) {
        const auto hash = Hash(key, visitors.seed);
        const auto bucket = static_cast<std::size_t>(hash >> (64 - visitors.precision));
        Insert(visitors, key);
        exact.insert(key);
        std::cout << "INSERT " << key << ": bucket " << bucket
                  << ", rank " << static_cast<int>(Rank(hash, visitors.precision))
                  << "; estimate " << Estimate(visitors) << ", exact " << exact.size() << '\n';
    }
    std::cout << "REGISTERS:";
    for (auto rank : visitors.registers) std::cout << ' ' << static_cast<int>(rank);
    std::cout << '\n';
    HyperLogLog left(4), right(4);
    for (const auto* key : {"alice", "bob", "alice"}) Insert(left, key);
    for (const auto* key : {"bob", "carol"}) Insert(right, key);
    std::cout << "\nMERGE: {alice, bob} UNION {bob, carol}\n"
              << "LEFT: estimate " << Estimate(left) << ", exact 2\n"
              << "RIGHT: estimate " << Estimate(right) << ", exact 2\n";
    Merge(left, right);
    std::cout << "UNION: estimate " << Estimate(left) << ", exact 3 (bob is not counted twice)\n";
    HyperLogLog large(14);
    for (int i = 0; i < 100000; ++i) Insert(large, "visitor" + std::to_string(i));
    const auto saved = large.registers;
    for (int i = 0; i < 100000; ++i) Insert(large, "visitor" + std::to_string(i));
    std::cout << "\nLARGER STREAM: 100000 distinct IDs, each inserted twice\n"
              << "p = 14, m = 16384; estimate " << Estimate(large) << ", exact 100000\n"
              << "SECOND PASS: registers " << (large.registers == saved ? "unchanged" : "changed") << '\n';
    return 0;
}
