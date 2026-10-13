# DSA-Style HyperLogLog in C++17

Estimate **how many distinct IDs appeared**, not how many events occurred, using a fixed array of small registers.

> [hyperloglog_dsa.cpp](hyperloglog_dsa.cpp) contains a dense, 64-bit **Insert / Estimate / Merge** core. It includes small-range linear counting, but is not HLL++, a production library, or Redis-compatible storage.

## Table of Contents

- [State and Procedures](#state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Build and Run](#build-and-run)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Complexity Breakdown](#complexity-breakdown)
- [Accuracy and Memory](#accuracy-and-memory)
- [Assumptions and Limits](#assumptions-and-limits)
- [References](#references)

## State and Procedures

| State/helper | Purpose |
| --- | --- |
| **precision p** | Bucket-selection bits; this code allows 4–18. |
| **m = 2^p registers** | One unsigned byte per bucket, initially zero. |
| **seed** | Fixed parameter for the same deterministic 64-bit hash throughout. |
| **Hash(key, seed)** | Byte accumulation and bit mixing; non-cryptographic teaching hash. |
| **Rank(hash, p)** | First 1-bit position in the remaining 64 − p bits, counting from 1. |

**Insert:** Select a bucket with the first p hash bits, then retain the maximum rank in that bucket. Rank is **leading-zero count + 1**, not the number of visits. An all-zero remainder has rank **65 − p**.

**Estimate:** Combine all registers using the scaled harmonic estimator. If the raw estimate is at most 2.5m and zero registers remain, use small-range linear counting.

**Merge:** Reject mismatched precision or seed before mutation; otherwise take the register-wise maximum. All callers also use this same code's hash algorithm, key bytes, and rank convention. A real interoperability check needs the full configuration, not only p and seed.

The exact `std::set` in the demonstration is ground truth only. No core procedure consults or stores it.

## Language-Neutral Pseudocode

```text
CREATE_HLL(p, seed):
    if p < 4 or p > 18:
        error "Unsupported precision"
    m = 2^p
    store fixed p and seed
    registers = m zeros
    return sketch

RANK(hash, p):
    remainder = hash bits AFTER the first p bucket bits
    return leading_zero_count(remainder) + 1
    // For an all-zero remainder: return (64 - p) + 1.

INSERT(sketch, key):
    h = HASH64(key, sketch.seed)
    j = integer represented by the first sketch.p bits of h
    r = RANK(h, sketch.p)
    registers[j] = MAX(registers[j], r)

ESTIMATE(sketch):
    m = length(registers)
    alpha = 0.673 if m = 16
            0.697 if m = 32
            0.709 if m = 64
            0.7213 / (1 + 1.079/m) otherwise
    sum = 0
    empty = 0
    for each r in registers:
        sum = sum + 2^(-r)
        if r = 0:
            empty = empty + 1
    raw = alpha * m * m / sum
    if raw <= 2.5*m and empty > 0:
        return m * LN(m / empty)
    return raw

MERGE(destination, source):
    if precision or seed differs:
        error "Incompatible sketches"
    for j = 0 to length(destination.registers) - 1:
        destination.registers[j] = MAX(destination.registers[j], source.registers[j])
```

The C++ rank helper checks precision before shifting and scans only the bounded remainder. It does not call a leading-zero intrinsic on zero. Configuration is immutable; do not edit or resize the register array outside the core procedures.

## Build and Run

From the **repository root**, use **Windows CMD**:

```bat
examples\hyperloglog\build.cmd
examples\hyperloglog\hyperloglog_dsa.exe
```

The script accepts no arguments and creates the executable **beside its source**, regardless of the working directory. Generated Windows and Unix binaries are ignored by Git.

Direct compilation:

```bat
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/hyperloglog/hyperloglog_dsa.cpp -o examples/hyperloglog/hyperloglog_dsa.exe
examples\hyperloglog\hyperloglog_dsa.exe
```

PowerShell, if executable launching is allowed in your environment:

```powershell
.\examples\hyperloglog\build.cmd
.\examples\hyperloglog\hyperloglog_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/hyperloglog/hyperloglog_dsa.cpp -o examples/hyperloglog/hyperloglog_dsa
./examples/hyperloglog/hyperloglog_dsa
```

## Illustrated Input and Output

**Input:** Run without arguments. Three demonstrations execute deterministically:

1. Six website visits from four distinct IDs, using 16 registers.
2. A union of two overlapping sets of visitors.
3. 100,000 distinct IDs inserted twice, using 16,384 registers.

**Output** (rounded to two decimal places; the final floating-point digit may vary slightly across platforms):

```text
p = 4, m = 16 registers, hash seed = 42
INITIAL: estimate 0.00
INSERT John_1275: bucket 1, rank 2; estimate 1.03, exact 1
INSERT David.raymond23: bucket 7, rank 1; estimate 2.14, exact 2
INSERT Sarah1978: bucket 1, rank 1; estimate 2.14, exact 3
INSERT John: bucket 1, rank 1; estimate 2.14, exact 4
INSERT John_1275: bucket 1, rank 2; estimate 2.14, exact 4
INSERT Sarah1978: bucket 1, rank 1; estimate 2.14, exact 4
REGISTERS: 0 2 0 0 0 0 0 1 0 0 0 0 0 0 0 0

MERGE: {alice, bob} UNION {bob, carol}
LEFT: estimate 1.03, exact 2
RIGHT: estimate 2.14, exact 2
UNION: estimate 2.14, exact 3 (bob is not counted twice)

LARGER STREAM: 100000 distinct IDs, each inserted twice
p = 14, m = 16384; estimate 101430.83, exact 100000
SECOND PASS: registers unchanged
```

**Why do four visitors estimate as 2.14?** The toy sketch has only two nonzero buckets: John_1275, Sarah1978, and John share bucket 1, whose maximum remains 2. There are **14 empty registers**, so linear counting gives:

$$
16\ln(16/14) \approx 2.14
$$

This is intentional evidence that a tiny sketch can be inaccurate, not a claim that HLL should return an exact integer. In the larger example it overestimates instead. Repeating existing IDs does not change the registers or estimate.

**Why not add the two counts?** The union contains alice, bob, and carol: **three** IDs. Register-wise maximum creates the same state as inserting all those IDs into a single sketch. It does not recover an exact count or a list of IDs.

See the [main notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#hyperloglog) for the hash-splitting diagram, formula explanation, and system-design usage table.

## Complexity Breakdown

Let m = 2^p be register count, L be key length in bytes, U be insertion calls, and K be sketches being merged.

| Operation/measure | Complexity | Reason |
| --- | --- | --- |
| **Initialize** | O(m) time | Allocate and zero all registers. |
| **Rank** | O(1) time and auxiliary space | At most 60 remainder bits for the supported 64-bit configuration. |
| **Insert** | O(1) with a fixed-size key/hash | One bucket and one maximum update. |
| **Actual string insertion** | O(L + 1) | Hash scans all key bytes; rank work is bounded. |
| **Estimate** | O(m) time | Scan all registers; no cached estimate here. |
| **Merge two sketches** | O(m) time | One maximum per corresponding register. |
| **Merge K sketches sequentially** | O(Km) time | Combine each source into a destination. |
| **Sketch storage** | O(m) bytes | m byte-sized registers plus constant-size configuration. |
| **Core operation auxiliary space** | O(1) | No extra arrays during Insert, Estimate, or Merge. |
| **U insertions** | O(U) for bounded-size keys | Stored state does not grow with the number of distinct IDs. |

These are parameterized costs. With fixed precision m is constant relative to stream length, but a larger precision still increases estimation/merge work and memory. Demo printing, exact-set maintenance, and the copied register snapshot have separate costs, excluded from the core's auxiliary-space bound.

## Accuracy and Memory

The raw estimator is:

$$
E = \alpha_m\frac{m^2}{\sum_j 2^{-M[j]}}
$$

It combines **2 raised to each rank** through a harmonic mean, not the ranks themselves. With suitable hashing, the customary relative-standard-error approximation is:

$$
\operatorname{RSE} \approx 1.04/\sqrt{m}
$$

This is statistical uncertainty, **not a guaranteed maximum error**, and is only a rough guide for tiny sketches and small-range regimes. The program's fixed hash is a teaching implementation, not a proof of the ideal random-hash assumptions. [Original HLL analysis](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)

For p = 14, m = 16,384, this approximation is **0.8125%**. The code stores **16 KiB** of registers, excluding object/allocation overhead. Six-bit packing would reduce register payload to **12 KiB**; this code keeps one byte per register for readability. Redis uses a packed dense layout and a sparse representation; this implementation does neither. [Redis representation](https://redis.io/docs/latest/commands/pfcount/)

The larger demo's **+1.43%** observed error is compatible with a standard error, which is not a hard ceiling. More registers generally reduce uncertainty; quadrupling their count approximately halves RSE.

## Assumptions and Limits

- **Insertion-only set summary:** Repeated identical byte strings leave state unchanged. There are no per-ID counts, membership queries, key enumeration, or ordinary deletion.
- **Compatible merges:** Fixed p, seed, hash, key encoding, and rank convention. Merge is commutative, associative, and idempotent; overlapping observations do not create extra distinct IDs.
- **Correct identity model:** For example, `Alice` and `alice` are different byte strings unless the caller normalizes them. “Distinct ID” does not automatically mean “distinct human.”
- **Intact state:** Registers hold valid bounded ranks. No external mutation, serialization from untrusted inputs, or concurrent writes are supported.
- **Non-cryptographic hashing:** No adversarial-input resistance, perfect hashing, privacy guarantee, or formal accuracy guarantee for this hash family is claimed.
- **Finite hash range:** Collisions eventually matter. No large-range saturation correction is implemented; do not treat the result as reliable near the 64-bit hash-space limit.
- **Limited estimator:** Dense registers and the classical small-range switch only. No HLL++ bias tables, sparse format, precision conversion, automatic windows, persistence, networking, or production-library compatibility. [HLL engineering variants](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
- **Validation:** Invalid p, incompatible merges, and executable arguments are rejected. The permitted p range is a deliberate teaching limit, not a universal HLL requirement.
- **Approximate analytics only:** Do not use HLL to enforce account uniqueness, calculate exact bills, or prove that a particular ID is absent.

## References

- [Flajolet, Fusy, Gandouet, and Meunier — HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf)
- [Google Research — HyperLogLog in Practice](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/)
- [Redis — HyperLogLog Data Type](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/)
- [Redis — PFCOUNT and Storage Representation](https://redis.io/docs/latest/commands/pfcount/)
