# DSA-Style Count-Min Sketch in C++17

Estimate **how many times a key appeared** using a fixed matrix of counters, rather than a growing exact key-to-count map.

> [count_min_sketch_dsa.cpp](count_min_sketch_dsa.cpp) implements **Update** and **Estimate** for nonnegative updates. It is a teaching example, not an exact counter, production library, or Redis-compatible implementation.

## Table of Contents

- [Core State and Procedures](#core-state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Build and Run](#build-and-run)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Complexity Breakdown](#complexity-breakdown)
- [Error and Sizing](#error-and-sizing)
- [Assumptions and Limits](#assumptions-and-limits)
- [References](#references)

## Core State and Procedures

| State | Meaning |
| --- | --- |
| `width` (w) | Counters per row; greater than zero. |
| `seeds` (d entries) | Fixed seeds selecting one hash function per row. |
| `counters` | d × w zero-initialized, unsigned 64-bit counters. |
| `total` (F) | Sum of all accepted update weights, not distinct-key count. |

**Update(key, weight):** Add the weight to **one counter in every row**, at `Hash(key, rowSeed) % w`. The default weight is 1. Even if two rows select the same column number, they update different cells.

**Estimate(key):** Read the key's selected counter in each row and return their **minimum**. For nonnegative updates and intact, non-overflowing state, collisions can add unrelated counts, so the estimate cannot be below the key's actual count. It may be above it.

There is no exact key list inside the sketch. The `std::map` in `main` is only demonstration ground truth; neither core procedure consults it.

## Language-Neutral Pseudocode

```text
CREATE_SKETCH(w, seeds):
    if w <= 0 or seeds is empty:
        error "Use positive width and depth"
    store fixed w and seeds
    counters = length(seeds) rows of w zero counters
    total = 0
    return sketch

UPDATE(sketch, key, increment = 1):
    if increment < 0:
        error "Negative updates are not supported"
    if increment == 0:
        return
    if total + increment would overflow:
        error "Total update weight would overflow"

    for row = 0 to length(sketch.seeds) - 1:
        col = HASH(key, sketch.seeds[row]) mod sketch.w
        counters[row][col] = counters[row][col] + increment
    total = total + increment

ESTIMATE(sketch, key):
    result = largest representable counter value
    for row = 0 to length(sketch.seeds) - 1:
        col = HASH(key, sketch.seeds[row]) mod sketch.w
        result = MIN(result, counters[row][col])
    return result
```

The overflow check uses `increment > MAX - total`, not an already-overflowed addition. Every cell is at most total under the supported update model, so checking total first protects all cells too. Rejected updates leave the sketch unchanged.

**Hashing helper:** Fixed 64-bit byte accumulation and bit mixing with a different seed per row. The five seeds `{6628, 589, 14217, 23745, 213}` reproduce the main notes' hash table for A–D. The function accepts arbitrary strings; no letter-specific hash-result table is hardcoded. These illustration-selected seeds do not establish the independence assumptions of the theoretical error bound.

## Build and Run

From the **repository root**, use **Windows CMD**:

```bat
examples\count_min_sketch\build.cmd
examples\count_min_sketch\count_min_sketch_dsa.exe
```

The build script creates the executable beside its source regardless of working directory, accepts no arguments, and generated binaries are ignored by Git.

Direct compilation:

```bat
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/count_min_sketch/count_min_sketch_dsa.cpp -o examples/count_min_sketch/count_min_sketch_dsa.exe
examples\count_min_sketch\count_min_sketch_dsa.exe
```

PowerShell, if executable launching is permitted in your environment:

```powershell
.\examples\count_min_sketch\build.cmd
.\examples\count_min_sketch\count_min_sketch_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/count_min_sketch/count_min_sketch_dsa.cpp -o examples/count_min_sketch/count_min_sketch_dsa
./examples/count_min_sketch/count_min_sketch_dsa
```

## Illustrated Input and Output

**Input:** Run without arguments. The program processes the stream **A, A, B, D, B, A, A, D, B, B**, displaying the first four updates and the final matrix. A second, deliberately narrow sketch demonstrates overestimation.

**Exact output:**

```text
w = 10 counters per row, d = 5 hash rows

INITIAL
col: 0 1 2 3 4 5 6 7 8 9
h1: 0 0 0 0 0 0 0 0 0 0
h2: 0 0 0 0 0 0 0 0 0 0
h3: 0 0 0 0 0 0 0 0 0 0
h4: 0 0 0 0 0 0 0 0 0 0
h5: 0 0 0 0 0 0 0 0 0 0

AFTER A
col: 0 1 2 3 4 5 6 7 8 9
h1: 1 0 0 0 0 0 0 0 0 0
h2: 0 0 1 0 0 0 0 0 0 0
h3: 0 0 0 0 1 0 0 0 0 0
h4: 0 0 0 0 0 0 0 0 1 0
h5: 0 0 0 0 0 0 0 0 0 1

AFTER A, A
col: 0 1 2 3 4 5 6 7 8 9
h1: 2 0 0 0 0 0 0 0 0 0
h2: 0 0 2 0 0 0 0 0 0 0
h3: 0 0 0 0 2 0 0 0 0 0
h4: 0 0 0 0 0 0 0 0 2 0
h5: 0 0 0 0 0 0 0 0 0 2

AFTER A, A, B
col: 0 1 2 3 4 5 6 7 8 9
h1: 2 1 0 0 0 0 0 0 0 0
h2: 0 0 2 1 0 0 0 0 0 0
h3: 0 0 0 0 3 0 0 0 0 0
h4: 0 0 0 0 0 0 0 1 2 0
h5: 0 0 1 0 0 0 0 0 0 2

AFTER A, A, B, D
col: 0 1 2 3 4 5 6 7 8 9
h1: 2 1 0 0 0 0 0 0 1 0
h2: 0 0 2 2 0 0 0 0 0 0
h3: 0 0 0 0 3 1 0 0 0 0
h4: 0 0 0 0 0 0 0 2 2 0
h5: 0 1 1 0 0 0 0 0 0 2
A: estimate 2, exact 2
B: estimate 1, exact 1
C: estimate 0, exact 0
D: estimate 1, exact 1

FINAL (10 events)
col: 0 1 2 3 4 5 6 7 8 9
h1: 4 4 0 0 0 0 0 0 2 0
h2: 0 0 4 6 0 0 0 0 0 0
h3: 0 0 0 0 8 2 0 0 0 0
h4: 0 0 0 0 0 0 0 6 4 0
h5: 0 2 4 0 0 0 0 0 0 4
A: estimate 4, exact 4
B: estimate 4, exact 4
C: estimate 0, exact 0
D: estimate 2, exact 2

FORCED COLLISIONS (w = 1, d = 2)
X: estimate 5, exact 3
Z: estimate 5, exact 0 (never inserted)
```

**Why take the minimum?** After A, A, B, D, A's selected counters are `[2, 2, 3, 2, 2]`. The third row includes B's contribution, but the minimum is still 2. B's counters are `[1, 2, 3, 2, 1]`, so its estimate is 1.

The estimates happen to be exact for these four letters. That is **not** guaranteed generally. In the one-column example, every row combines X's three occurrences and Y's two: X is overestimated as 5, and even never-inserted Z is estimated as 5. More rows cannot fix a sketch in which every row collides.

The matrices follow the supplied hash-position table, correcting missing/misplaced entries in the textbook screenshots. See the [main notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#count-min-sketch) for the table and Mermaid matrix.

## Complexity Breakdown

Let w be width, d be depth, L be key length in bytes, and U be the number of update calls.

| Measure | Complexity | Reason |
| --- | --- | --- |
| **Initialize** | O(dw + d) time | Zero dw counters and store d seeds. |
| **Update** | O(d) assuming O(1) hashing | Increment one cell per row; zero-weight updates return immediately. |
| **Estimate** | O(d) assuming O(1) hashing | Read one cell per row and take the minimum. |
| **Actual string hashing** | O(d(L + 1)) per nonzero update or query | Each seeded hash scans the key bytes. |
| **Sketch storage** | O(dw + d) words = O(dw) | dw 64-bit counters, d 64-bit seeds, and total; w ≥ 1. |
| **Operation auxiliary space** | O(1) | Hash accumulator, row/column indices, and result. |
| **U updates** | O(Ud) under constant-time hashing | Storage does not grow with the number of distinct keys. |

For fixed d and bounded-size keys, updates and queries are O(1) with respect to stream length. Printing a full matrix takes O(dw), and the demo's exact map has separate costs; neither belongs to the core Update/Estimate complexity.

## Error and Sizing

For nonnegative counts, a standard sizing choice is:

$$
w = \left\lceil \frac{e}{\varepsilon} \right\rceil,
\qquad d = \left\lceil \ln\frac{1}{\delta} \right\rceil
$$

For a fixed queried key x, suitable independently chosen row hashes give:

$$
f_x \le \widehat{f}_x \le f_x + \varepsilon F
$$

with probability at least $1-\delta$, where F is total update weight. The lower bound follows from nonnegative collisions; the probabilistic part is the additive upper-error bound. It is not an error percentage of $f_x$ itself. [Original Count-Min Sketch analysis](https://www.cs.ox.ac.uk/people/graham.cormode/pubs/papers/cm-full.pdf)

The toy hash family and example-selected seeds are not a proof of that probability guarantee. A production design must use a suitable hash family and validate its workload.

## Assumptions and Limits

- **Nonnegative updates only:** Each call accepts a signed 64-bit increment from 0 to `INT64_MAX`; negative updates throw `std::invalid_argument`. Other stream models need separately justified methods.
- **No silent overflow:** Counters and total are unsigned 64-bit. An update that would overflow total throws `std::overflow_error` before any cell changes. State must remain intact; do not edit counters outside Update.
- **Fixed configuration:** Width, ordered seeds, hash function, and key encoding do not change. Use appropriate distinct seeds; duplicate seeds are accepted but provide redundant rows.
- **No exact membership or enumeration:** A positive estimate does not prove an item appeared; the matrix cannot list its keys or find all top items by itself.
- **No aging:** Counts accumulate indefinitely. Sliding windows or decay require extra machinery.
- **No networking, persistence, concurrency, or merge API:** Compatible sketches can conceptually merge by adding corresponding counters and totals, with the same dimensions and hashes. That operation is described in the notes, not implemented here.
- **Duplicate events count again:** Event deduplication is outside the sketch; summing overlapping streams also double-counts their shared events.
- **Valid keys:** Empty strings and arbitrary byte strings are allowed. Zero width or an empty seed list is rejected; unsupported executable arguments return a nonzero exit code.
- **Teaching scope:** No cryptographic resistance, formal hash-family guarantee, or production-library compatibility is claimed.

## References

- [Graham Cormode and S. Muthukrishnan — An Improved Data Stream Summary: The Count-Min Sketch and its Applications](https://www.cs.ox.ac.uk/people/graham.cormode/pubs/papers/cm-full.pdf)
- [Redis — Count-Min Sketch Data Type](https://redis.io/docs/latest/develop/data-types/probabilistic/count-min-sketch/)
