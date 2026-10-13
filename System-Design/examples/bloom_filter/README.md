# DSA-Style Bloom Filter in C++17

Use a **packed bit array and multiple hashes** to answer: **definitely absent, or possibly present?**

> [bloom_filter_dsa.cpp](bloom_filter_dsa.cpp) implements the insertion-only core with two short procedures: **Insert** and **MayContain**. It is a teaching example, not a username-registration service or production filter library.

## Table of Contents

- [Core State and Procedures](#core-state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Build and Run](#build-and-run)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Complexity Breakdown](#complexity-breakdown)
- [Sizing and False Positives](#sizing-and-false-positives)
- [Assumptions and Limits](#assumptions-and-limits)
- [References](#references)

## Core State and Procedures

| State | Meaning |
| --- | --- |
| `bitCount` ($m$) | Number of usable bits, greater than zero. |
| `seeds` ($k$ entries) | Fixed seeds selecting the hash functions; at least one seed. |
| `words` | Zero-initialized packed storage: bit p is in word `p / 64`, at offset `p % 64`. |

Each hash chooses a position `Hash(key, seed) % m`. The seed, hash function, byte encoding, and bit count must stay the same between insertion and lookup.

| Procedure | Meaning |
| --- | --- |
| **Insert** | Set each of the key's k selected bits to 1. Shared positions stay 1. |
| **MayContain** | Return `false` if any selected bit is 0; otherwise return `true`. |

`true` means **possibly present**, not “found.” The filter stores no original keys and cannot retrieve or enumerate them.

## Language-Neutral Pseudocode

```text
CREATE_FILTER(m, seeds):
    if m <= 0 or seeds is empty:
        error "Use positive bit count and at least one hash seed"
    store fixed m and seeds
    bits = m zero bits
    return filter

INSERT(filter, key):
    for each seed in filter.seeds:
        p = HASH(key, seed) mod filter.m
        filter.bits[p] = 1

MAY_CONTAIN(filter, key):
    for each seed in filter.seeds:
        p = HASH(key, seed) mod filter.m
        if filter.bits[p] == 0:
            return false  // Definitely absent from the represented set.
    return true          // Possibly present; verify when exactness matters.
```

The C++ version implements the conceptual bit array with `std::vector<std::uint64_t>`, not one byte per bit. It allocates `ceil(m / 64)` words; unused trailing bits are never queried.

**Hashing helper:** The code uses fixed unsigned 64-bit byte accumulation followed by bit mixing. Seeds `100824` and `12406` were selected to reproduce the illustrative username positions below. There are **no username-specific branches or stored hash-result tables**: the same function accepts arbitrary strings, including the empty string. These seeds and this non-cryptographic helper are for the demonstration, not production tuning or adversarial inputs.

## Build and Run

From the **repository root**, use **Windows CMD**:

```bat
examples\bloom_filter\build.cmd
examples\bloom_filter\bloom_filter_dsa.exe
```

The build script produces `bloom_filter_dsa.exe` beside its source regardless of the working directory. It accepts no arguments; generated binaries are ignored by Git.

Direct compilation:

```bat
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/bloom_filter/bloom_filter_dsa.cpp -o examples/bloom_filter/bloom_filter_dsa.exe
examples\bloom_filter\bloom_filter_dsa.exe
```

PowerShell, if executable launching is permitted in your environment:

```powershell
.\examples\bloom_filter\build.cmd
.\examples\bloom_filter\bloom_filter_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/bloom_filter/bloom_filter_dsa.cpp -o examples/bloom_filter/bloom_filter_dsa
./examples/bloom_filter/bloom_filter_dsa
```

## Illustrated Input and Output

**Input:** Run without arguments. The program creates a 10-bit filter with two hashes, inserts `john`, `dave`, and `peter`, then queries `donald`, `sarah`, and `john`.

**Exact output:**

```text
m = 10 bits, k = 2 hash functions
INITIAL: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
INSERT john (5, 8): [0, 0, 0, 0, 0, 1, 0, 0, 1, 0]
INSERT dave (3, 5): [0, 0, 0, 1, 0, 1, 0, 0, 1, 0]
INSERT peter (2, 9): [0, 0, 1, 1, 0, 1, 0, 0, 1, 1]

QUERY donald (3, 7): DEFINITELY ABSENT; exact set: absent
QUERY sarah (3, 8): POSSIBLY PRESENT; exact set: absent (false positive)
QUERY john (5, 8): POSSIBLY PRESENT; exact set: present
```

**Why these results occur:**

- **donald:** Bit 7 is 0. If donald had been inserted, that bit would be 1. It is therefore definitely absent from the represented set.
- **sarah:** Bits 3 and 8 are already 1 because of dave and john. The filter cannot tell who set them. This is a **false positive**: sarah was never inserted.
- **john:** Both of its bits remain 1. The filter returns possibly present, and the separate exact set confirms that it is present.

The `std::set` in `main` is **demonstration ground truth only**. `Insert` and `MayContain` do not access it. Displaying the bit array is also demonstration work, not part of the membership algorithm.

> **Username safety:** A positive result needs an exact lookup. Even a negative result does not reserve a username: another request may claim it concurrently. The database must enforce uniqueness atomically.

## Complexity Breakdown

Let $m$ be the bit count, $k$ the number of hash seeds, $n$ the number of distinct inserted keys, and $L$ the queried key length in bytes.

| Measure | Complexity | Reason |
| --- | --- | --- |
| **Initialize packed storage** | O(ceil(m / 64) + k) time | Zero all words and store k seeds. |
| **Insert** | O(k) assuming O(1) hashing | Compute k positions and set k bits. |
| **MayContain** | O(k) worst case assuming O(1) hashing | Check up to k bits; it can exit at the first 0. |
| **Actual string hashing in this code** | O(k(L + 1)) time per insertion or worst-case query | Each seeded hash scans the bytes and performs fixed bit mixing. |
| **Filter storage** | m bits rounded to 64-bit words, plus k 64-bit seeds | O(m + k) bits, treating word width as fixed; no n-key collection. |
| **Operation auxiliary space** | O(1) | One hash accumulator and one position at a time. |

For fixed k and bounded-size keys, insertion and membership queries are **O(1) with respect to n**. This does not mean the filter remains accurate as n grows: its bits fill up and false positives increase.

The exact set used for the demo has its own storage and lookup costs; it is excluded from the **filter-core** complexity.

## Sizing and False Positives

Under the usual well-distributed, approximately independent hashing assumptions, the false-positive probability for a key not in the set is approximately:

$$
p \approx \left(1-e^{-kn/m}\right)^k
$$

For a planned n and target p:

$$
m \approx -\frac{n\ln p}{(\ln 2)^2},
\qquad
k_{\mathrm{opt}} \approx \frac{m}{n}\ln 2
$$

Choose an integer k near the optimum and budget enough bits for the expected number of **distinct** keys. These estimates guide sizing; they do not certify the example's custom hash family or exact behavior of a tiny 10-bit filter. [Hash-based techniques and Bloom-filter analysis](https://www.eecs.harvard.edu/~michaelm/postscripts/dimacs-chapter-08.pdf)

- **More bits** generally lower false positives at fixed n and k, but consume more memory.
- **More hashes are not always better:** Beyond the optimum, extra hashes fill too many bits, raising false positives as well as CPU cost.
- **More distinct inserted keys** increase saturation at fixed m and k. Reinserting the same key changes no bits.

For the full username table, a Mermaid decision diagram, use cases, and a sizing example, see the [Bloom Filters notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#bloom-filters).

## Assumptions and Limits

- **Insertion only:** No deletion or bit clearing. Clearing dave's bit 5 would also remove evidence needed for john, creating a false negative.
- **Completed, correctly synchronized operations:** No concurrent access or partially visible insertion. Real shared filters require suitable synchronization.
- **Fixed configuration and intact bits:** No false negatives for successfully inserted keys under these conditions. A stale filter may miss keys in a newer database; that is not an accurate representation of that database.
- **Hash quality:** Use distinct, suitable seeds/functions. Duplicate seeds are accepted by this short implementation but give redundant probes; the theoretical analysis assumes appropriate hashing, not merely a list of seeds.
- **No exact membership:** Positives need authoritative verification for exact deduplication, security decisions, or username availability.
- **No distributed integration:** No database synchronization, persistence, sockets, filter resizing, or data recovery. Rebuild from the authoritative set or use an appropriate variant when capacity or deletion requirements change.
- **Validation:** Zero bits or an empty seed list throws `std::invalid_argument`. The empty string is a valid key. Unsupported executable arguments return a nonzero exit code.
- **Teaching scope:** The filter does not claim RocksDB compatibility, cryptographic resistance, or a measured production false-positive rate.

## References

- [Adam Kirsch, Michael Mitzenmacher, and George Varghese — Hash-Based Techniques for High-Speed Packet Processing](https://www.eecs.harvard.edu/~michaelm/postscripts/dimacs-chapter-08.pdf)
- [RocksDB — Bloom Filter Design and Database Use](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)
