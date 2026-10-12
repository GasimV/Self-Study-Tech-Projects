# DSA-Style Consistent Hashing in C++17

Use a **hash ring with virtual nodes** to assign keys to servers while limiting reassignment when a server joins or leaves.

> [consistent_hashing_dsa.cpp](consistent_hashing_dsa.cpp) is an independently written, dependency-free teaching implementation of the established algorithm—not a production storage system or a drop-in Envoy/bRPC component.

## Table of Contents

- [Core State and Procedures](#core-state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Build and Run](#build-and-run)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Complexity Breakdown](#complexity-breakdown)
- [Industry Implementations](#industry-implementations)
- [Assumptions and Limits](#assumptions-and-limits)
- [References](#references)

## Core State and Procedures

| State | Meaning |
| --- | --- |
| `virtualNodes` | Fixed number of tokens per physical server; greater than zero. |
| `tokens` | Ordered map: `(hash position, token ID)` → physical server ID. |
| `servers` | Set of physical server IDs, preventing duplicate additions. |

Each server gets token IDs such as `server0#0`, `server0#1`, and so on. Hash these IDs into the **same fixed 64-bit space** used for keys. Adding servers does not change the hash function or existing token positions.

| Procedure | Core operation |
| --- | --- |
| **AddServer** | Insert all of a server's virtual-node tokens. Return `false` if the server already exists. |
| **RemoveServer** | Remove all of that server's tokens. Return `false` if it was not a member. |
| **GetServer** | Find the first token at or after the key's hash; wrap to the first token if necessary. Return `NONE` for an empty ring. |

**Collision rule:** Different token IDs may have the same hash position. Keep both tokens, sorting by position **then token ID**, rather than overwriting one. A key exactly at that position selects the lexicographically first token ID there. All callers must use this same tie-breaking rule.

> **Virtual nodes are not extra machines or replicas.** Four tokens for server0 still route to the same physical server0.

## Language-Neutral Pseudocode

The ordered map compares pairs lexicographically. `LOWER_BOUND` returns the first entry whose map key is greater than or equal to the search pair. Server IDs are nonempty; token IDs use a fixed encoding of `server + "#" + decimal(i)`.

```text
CREATE_RING(V):
    if V <= 0:
        error "Use at least one token per server"
    return ring(V, empty ordered map, empty membership set)

ADD_SERVER(ring, server):
    if server is empty:
        error "Server ID must not be empty"
    if server already exists in ring.servers:
        return false
    insert server into ring.servers

    for i = 0 to ring.V - 1:
        id = server + "#" + decimal(i)
        ring.tokens[(HASH(id), id)] = server
    return true

REMOVE_SERVER(ring, server):
    if server does not exist in ring.servers:
        return false
    erase server from ring.servers

    for i = 0 to ring.V - 1:
        id = server + "#" + decimal(i)
        erase (HASH(id), id) from ring.tokens
    return true

GET_SERVER(ring, key):
    if ring.tokens is empty:
        return NONE
    entry = LOWER_BOUND(ring.tokens, (HASH(key), ""))
    if entry does not exist:
        entry = FIRST(ring.tokens)
    return entry.server
```

**Hashing helper:** `Hash` processes the input bytes with fixed unsigned 64-bit arithmetic and then mixes the bits. It is deterministic and non-cryptographic. The pseudocode treats it as a helper so the **placement algorithm** stays clear. Reproducing the exact sample output requires the helper and byte encoding in this C++ file, not an arbitrary replacement hash.

## Build and Run

From the **repository root**, use **Windows CMD**:

```bat
examples\consistent_hashing\build.cmd
examples\consistent_hashing\consistent_hashing_dsa.exe
```

The script always writes `consistent_hashing_dsa.exe` beside its source, regardless of the working directory. It accepts no arguments. Generated binaries are ignored by Git.

Direct compilation from the repository root:

```bat
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/consistent_hashing/consistent_hashing_dsa.cpp -o examples/consistent_hashing/consistent_hashing_dsa.exe
examples\consistent_hashing\consistent_hashing_dsa.exe
```

PowerShell, if executable launching is permitted in your environment:

```powershell
.\examples\consistent_hashing\build.cmd
.\examples\consistent_hashing\consistent_hashing_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/consistent_hashing/consistent_hashing_dsa.cpp -o examples/consistent_hashing/consistent_hashing_dsa
./examples/consistent_hashing/consistent_hashing_dsa
```

## Illustrated Input and Output

**Input:** Run the executable without arguments. The built-in demonstration:

1. Adds server0–server3, with **four tokens per server**.
2. Looks up five customer keys.
3. Adds server4 and repeats those lookups.
4. Removes server1 from that five-server ring and repeats them again.

**Exact output:**

```text
INITIAL (4 servers, 16 tokens)
  customer1 -> server1
  customer2 -> server3
  customer4 -> server2
  customer6 -> server0
  customer12 -> server0

AFTER ADD server4 (5 servers, 20 tokens)
  customer1 -> server1
  customer2 -> server3
  customer4 -> server2
  customer6 -> server0
  customer12 -> server4 (moved from server0)

AFTER REMOVE server1 (4 servers, 16 tokens)
  customer1 -> server2 (moved from server1)
  customer2 -> server3
  customer4 -> server2
  customer6 -> server0
  customer12 -> server4
```

**What happened?**

- **Join:** A server4 token becomes customer12's next clockwise token. The other illustrated keys retain their owners.
- **Leave:** Removing server1's tokens makes server2 the next clockwise owner of customer1. Keys owned by other servers stay put.
- **Not every key moves:** Existing servers keep their tokens; ownership changes only where the clockwise successor changes.

These are **five selected keys**, not a measurement of the entire workload or a promise of equal distribution. The hash positions differ from the simplified `0–99` example in the main notes.

> “Moved” means **the owner returned by the algorithm changed**. This program does not store or transfer customer records.

## Complexity Breakdown

Let $N$ be the number of physical servers, $V$ the fixed number of virtual nodes per server, and $T = NV$ the total number of ring tokens. Assume bounded-size identifiers and constant-time hashing for this table.

| Operation / measure | Complexity | Reason |
| --- | --- | --- |
| **GetServer** | O(log T) time for a nonempty ring | `std::map::lower_bound` searches the ordered tree; wrapping takes O(1). |
| **AddServer** | O(V log(T + V)) time | Insert V tokens plus physical membership. |
| **RemoveServer** | O(V log T) time for an existing server | Recompute and erase V token keys plus physical membership. |
| **Build N-server ring through additions** | O(T log T) time | Insert T tokens into the ordered map. |
| **Ring storage** | O(T + N) = O(T) | One entry per token plus physical membership, with V ≥ 1. |
| **GetServer auxiliary space** | O(1) | One iterator and a fixed-size search key under the bounded-identifier assumption. |

For empty or very small rings, interpret logarithmic bounds as `log(T + 1)`; empty lookup is O(1). A duplicate addition or missing-server removal only performs the membership-set operation, O(log(N + 1)).

**Variable-length strings:** Hashing a key of $K$ bytes costs O(K); returned server strings must also be copied. Token-ID construction, hashing, and string comparison have length-dependent costs too. The table isolates the data-structure costs rather than hiding these assumptions.

This is **local computational complexity**, not network latency or data-migration cost. A membership change can require moving many records even though updating the token map is cheap.

## Industry Implementations

Ready-made C++ implementations exist in established infrastructure projects:

| Project | Implementation | What to look for |
| --- | --- | --- |
| **Envoy** | [Ring-hash C++ source](https://github.com/envoyproxy/envoy/blob/main/source/extensions/load_balancing_policies/ring_hash/ring_hash_lb.cc) | Virtual-node ring construction, sorting, and binary-search host selection. |
| **Apache bRPC** | [Consistent-hashing C++ source](https://github.com/apache/brpc/blob/master/src/brpc/policy/consistent_hashing_load_balancer.cpp) | Virtual-node construction, server membership updates, and hashing policies including Ketama. |

These are **framework components**, with dependencies and operational behavior beyond a short DSA example. Envoy also documents [ring-hash load balancing](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers.html#ring-hash); bRPC documents [consistent-hashing client policies](https://github.com/apache/brpc/blob/master/docs/en/client.md#c_murmurhash-or-c_md5).

**Why this example is separate:** It implements the same core idea using only C++17 standard-library containers. It uses an ordered tree rather than Envoy's sorted-vector ring and deliberately omits production integration. It does **not** reproduce either project's hash values, configuration, or routing compatibility.

For learning, start here and then inspect those production sources. For production, evaluate an established implementation within the intended framework instead of treating this teaching example as ready infrastructure. If directly adapting upstream code, preserve its applicable license and attribution notices.

## Assumptions and Limits

- **Stable identity:** Server IDs, hash function, byte encoding, token-count policy, and collision ordering are fixed and shared by callers.
- **Single process:** Membership changes are explicit and sequential. No networking, concurrent mutation, discovery, health checks, or coordinated configuration rollout.
- **Memory only:** No persistence, data transfer, replicas, recovery, or durable storage.
- **Equal token counts:** All servers receive V tokens. Weighted placement and production ring-sizing policies are omitted.
- **Balance is approximate:** Four tokens per server illustrate the algorithm, not a recommended production configuration. More tokens do not guarantee equal traffic or solve a single hot key.
- **Safe input assumptions:** IDs use the same bytes everywhere. The teaching hash is not cryptographic or intended to resist maliciously selected keys.
- **Explicit edge cases:** Empty rings return `std::nullopt`; duplicate additions and absent removals return `false`; zero tokens per server and empty added server IDs throw `std::invalid_argument`. An empty lookup key is allowed.

> **Placement is not replication or consensus.** The ring identifies an owner; other mechanisms keep its data available and ensure all routers use the appropriate membership view.

See the fuller [Consistent Hashing notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#consistent-hashing).

## References

- [David Karger and colleagues — Consistent Hashing and Random Trees](https://people.csail.mit.edu/karger/Papers/web.pdf)
- [Envoy — Ring-Hash Load Balancing](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/upstream/load_balancing/load_balancers.html#ring-hash)
- [Envoy — Ring-Hash C++ Implementation](https://github.com/envoyproxy/envoy/blob/main/source/extensions/load_balancing_policies/ring_hash/ring_hash_lb.cc)
- [Apache bRPC — Consistent-Hashing C++ Implementation](https://github.com/apache/brpc/blob/master/src/brpc/policy/consistent_hashing_load_balancer.cpp)
- [Apache bRPC — Client Load-Balancing Policies](https://github.com/apache/brpc/blob/master/docs/en/client.md#c_murmurhash-or-c_md5)
