# DSA-Style Classical Byzantine Agreement in C++17

[bft_dsa.cpp](bft_dsa.cpp) implements the recursive **Oral Messages algorithm, OM(m)**: a commander sends an order, lieutenants relay what they received, and each combines the reports into a decision.

> **BFT is a property, not one algorithm.** This example teaches the classical generals algorithm—not PBFT, blockchain consensus, or a replicated log. `ATTACK` and `RETREAT` are symbolic textbook values; the program performs no physical action.

## Table of Contents

- [Build and Run](#build-and-run)
- [Roles, State, and Procedures](#roles-state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Why Agreement Works](#why-agreement-works)
- [Complexity Breakdown](#complexity-breakdown)
- [Assumptions and Limits](#assumptions-and-limits)
- [Verification](#verification)
- [References](#references)

## Build and Run

From the **repository root**, in **Command Prompt (CMD)**, with `g++` on your `PATH`:

```bat
.\examples\bft\build.cmd
.\examples\bft\bft_dsa.exe
```

The build script creates `examples/bft/bft_dsa.exe` beside its source, independent of the working directory. From inside that folder, use `.\build.cmd` and `.\bft_dsa.exe`. The executable runs all four demonstrations and takes no arguments. Unsupported build or executable arguments print usage and fail.

Direct compilation:

```bat
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/bft/bft_dsa.cpp -o examples/bft/bft_dsa.exe
```

The same commands can be entered in PowerShell, but local application-control rules may affect launching. If execution is blocked, report the message to the administrator; do not disable security controls. CMD is listed first because it worked in the earlier examples on this machine.

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/bft/bft_dsa.cpp -o examples/bft/bft_dsa
./examples/bft/bft_dsa
```

No external libraries are needed. Generated Windows and Unix executables are ignored by [.gitignore](.gitignore).

## Roles, State, and Procedures

| Concept | Meaning in the implementation |
| --- | --- |
| **Commander** | Sends the order for the current recursive call. A lieutenant becomes a commander when relaying its report. |
| **Lieutenant** | Receives an order and, when depth permits, relays it to the other lieutenants. |
| **N** | Fixed participant count. IDs are distinct by construction: `0..N-1`. In the demonstration, A=0, B=1, C=2, D=3. |
| **m** | Configured maximum Byzantine fault count and recursion depth—not the measured number of traitors. |
| `group` | The current commander first, followed by its lieutenants. Previous commanders are excluded from recursive groups. |
| `path` | Commander IDs along the recursive branch. `A -> B -> C` means B is telling C what B claims A sent. |
| `received[i]` | Lieutenant i's direct order for this call, with omissions defaulted to `RETREAT`. |
| `reports[j][i]` | Recipient j's report from lieutenant i. The diagonal contains each recipient's own direct order. |
| `Transport` | A simulator callback returning the message or an omission. It can inject a faulty sender's lies. |

| Procedure | Responsibility |
| --- | --- |
| `Receive` | Request one message from the expected sender; use `RETREAT` if missing. |
| `Majority` | Return the strict binary majority; ties or an empty list return `RETREAT`. |
| `Relay` | Recursively perform OM(m) and combine each recipient's reports. |
| `OralMessages` | Validate inputs, form membership, invoke recursion, and return decisions indexed by participant ID. |

The top-level commander's result is empty: this version defines **lieutenant decisions**. Recursive `Relay` results instead follow the current group's lieutenant order.

**The agreement procedure does not know who is faulty.** Only the injected message behavior and demonstration reporting use that information. Displaying only loyal decisions is a simulator diagnostic, not a traitor-detection technique. The simulator does not model a faulty node's private computation; its outgoing reports can still be arbitrary.

## Language-Neutral Pseudocode

`SEND` is the simulated transport. Loyal senders transmit the supplied order; faulty senders may send either order or omit it. A receiver knows the immediate sender, but cannot verify that a relayed claim is truthful.

```text
RECEIVE(sender, receiver, order, path, SEND):
    message = SEND(sender, receiver, order, path)
    return message if present, otherwise RETREAT

MAJORITY(reports):
    if count(ATTACK in reports) > length(reports) / 2:
        return ATTACK
    return RETREAT

RELAY(depth, group, order, SEND, path):
    append group[0] to path
    k = length(group) - 1
    for i = 0 .. k-1:
        received[i] = RECEIVE(group[0], group[i+1], order, path, SEND)

    if depth == 0:
        remove last ID from path
        return received

    create k-by-k reports matrix
    for i = 0 .. k-1:
        reports[i][i] = received[i]
        child = [group[i+1]] followed by all other lieutenants
        relayed = RELAY(depth-1, child, received[i], SEND, path)
        next = 0
        for j = 0 .. k-1, excluding i:
            reports[j][i] = relayed[next]
            next = next + 1

    for i = 0 .. k-1:
        received[i] = MAJORITY(reports[i])
    remove last ID from path
    return received

ORAL_MESSAGES(N, m, commander, order, SEND):
    require N >= 2 and 0 <= m <= N-2
    require 0 <= commander < N, a valid order, and a transport
    group = [commander] followed by all other IDs in ascending order
    decisions = RELAY(m, group, order, SEND, empty path)
    result = N empty positions
    map decisions to their corresponding lieutenant IDs in result
    return result
```

Each expected sender/path is visited once. Repeated arbitrary replies cannot inflate the vote count; asynchronous duplicate-message processing is not implemented.

> **OM(1) is not simply a vote on the commander's direct messages.** There is a direct-message round, then a relay round. Each lieutenant includes its own direct order and the other lieutenants' reports before deciding.

## Illustrated Input and Output

The inputs are supplied by `main()`: four participants, commander A, `m=1`, and the four message behaviors below. All scenarios are independent; no decision carries into the next one.

| Scenario | Injected behavior | Expected loyal decisions |
| --- | --- | --- |
| All loyal | A sends `ATTACK`; all relays preserve it. | B=C=D=`ATTACK` |
| Dishonest lieutenant D | A sends `ATTACK`; D tells B `RETREAT` and C `ATTACK`. | B=C=`ATTACK` |
| Dishonest commander A | A tells B `ATTACK`, C `RETREAT`, and D `ATTACK`. | B=C=D=`ATTACK` |
| Two traitors A and D | Both tell B `ATTACK` and C `RETREAT`. | B=`ATTACK`, C=`RETREAT` |

Exact program output:

```text
SCENARIO: all loyal
N=4, OM(1), configured fault budget=1
FAULTY: none
GUARANTEE: within configured fault bound
  DIRECT A -> B: ATTACK
  DIRECT A -> C: ATTACK
  DIRECT A -> D: ATTACK
  RELAY  A -> B -> C: ATTACK
  RELAY  A -> B -> D: ATTACK
  RELAY  A -> C -> B: ATTACK
  RELAY  A -> C -> D: ATTACK
  RELAY  A -> D -> B: ATTACK
  RELAY  A -> D -> C: ATTACK
LOYAL LIEUTENANT DECISIONS:
  B = ATTACK
  C = ATTACK
  D = ATTACK
RESULT: loyal lieutenants agree on ATTACK

SCENARIO: dishonest lieutenant D
N=4, OM(1), configured fault budget=1
FAULTY: D
GUARANTEE: within configured fault bound
  DIRECT A -> B: ATTACK
  DIRECT A -> C: ATTACK
  DIRECT A -> D: ATTACK
  RELAY  A -> B -> C: ATTACK
  RELAY  A -> B -> D: ATTACK
  RELAY  A -> C -> B: ATTACK
  RELAY  A -> C -> D: ATTACK
  RELAY  A -> D -> B: RETREAT
  RELAY  A -> D -> C: ATTACK
LOYAL LIEUTENANT DECISIONS:
  B = ATTACK
  C = ATTACK
RESULT: loyal lieutenants agree on ATTACK

SCENARIO: dishonest commander A
N=4, OM(1), configured fault budget=1
FAULTY: A
GUARANTEE: within configured fault bound
  DIRECT A -> B: ATTACK
  DIRECT A -> C: RETREAT
  DIRECT A -> D: ATTACK
  RELAY  A -> B -> C: ATTACK
  RELAY  A -> B -> D: ATTACK
  RELAY  A -> C -> B: RETREAT
  RELAY  A -> C -> D: RETREAT
  RELAY  A -> D -> B: ATTACK
  RELAY  A -> D -> C: ATTACK
LOYAL LIEUTENANT DECISIONS:
  B = ATTACK
  C = ATTACK
  D = ATTACK
RESULT: loyal lieutenants agree on ATTACK

SCENARIO: two traitors A and D
N=4, OM(1), configured fault budget=1
FAULTY: A D
GUARANTEE: outside the fault guarantee
  DIRECT A -> B: ATTACK
  DIRECT A -> C: RETREAT
  DIRECT A -> D: RETREAT
  RELAY  A -> B -> C: ATTACK
  RELAY  A -> B -> D: ATTACK
  RELAY  A -> C -> B: RETREAT
  RELAY  A -> C -> D: RETREAT
  RELAY  A -> D -> B: ATTACK
  RELAY  A -> D -> C: RETREAT
LOYAL LIEUTENANT DECISIONS:
  B = ATTACK
  C = RETREAT
RESULT: loyal lieutenants disagree
```

## Why Agreement Works

**One dishonest lieutenant:** With loyal A sending `ATTACK`, B combines its direct `ATTACK`, C's truthful `ATTACK`, and D's false `RETREAT`. The two truthful reports win. C also decides `ATTACK`.

**Dishonest commander:** B, C, and D are loyal, so their relays let each assemble the same reports: `ATTACK`, `RETREAT`, `ATTACK`. All choose `ATTACK`, despite receiving different direct orders.

**Two traitors:** B combines `ATTACK`, `RETREAT`, `ATTACK`; C combines `ATTACK`, `RETREAT`, `RETREAT`. They disagree. This is one concrete failure beyond the configured fault limit—not a claim that every outside-bound run must fail.

| Guarantee | Meaning |
| --- | --- |
| **Agreement** | All loyal lieutenants obtain the same decision. |
| **Validity** | If the commander is loyal, each loyal lieutenant obtains its order. |

OM(m) guarantees both when **N >= 3m + 1**, at most **m** participants are faulty, and the communication assumptions hold. A faulty commander has no trustworthy intended order to preserve. The selected order is not necessarily wise or factually correct. [Original algorithm and guarantees](https://lamport.azurewebsites.net/pubs/byz.pdf)

## Complexity Breakdown

For **N participants**, recursion depth **m**, and constant-size orders:

| Measure | Bound |
| --- | --- |
| `Receive` | O(1) work, assuming constant-time transport without trace formatting |
| `Majority` on k reports | O(k) time; O(1) additional space |
| Message deliveries and local agreement work | O(N^(m+1)) upper bound |
| Sequential matrix-based auxiliary storage | O((m+1)N²) upper bound; OM(0) needs only O(N) |
| Top-level result storage | O(N) |
| Synchronous communication rounds | m + 1 |
| OM(1) | O(N²) work/messages and O(N²) auxiliary storage |

There are `N-1` direct messages, then `(N-1)(N-2)` relays, and further decreasing-factor products for deeper recursion. OM(1) with four participants delivers **3 + 6 = 9 messages**; OM(2) with seven delivers **6 + 30 + 120 = 156**.

Each non-base call keeps its report matrix while processing children **one at a time**. At most `m+1` calls are active; this gives the stated conservative storage bound, rather than storing the entire message tree. Paths are extended and shortened in place.

These bounds exclude console trace formatting and any storage a custom transport retains. Printing a path costs additional work proportional to its length. Increasing m is expensive; this classical algorithm is not an efficient replacement for practical replicated-service protocols.

**Rounds are not wall-clock milliseconds.** The synchronous model needs a known delivery/round bound so absent messages can be recognized. Synchronous function calls simulate those rounds; they do not implement real network deadlines.

## Assumptions and Limits

- **Known senders:** No participant can impersonate another sender. A relayed claim can still be false; no digital signatures are used to prove earlier message contents.
- **Reliable communication:** Sent messages arrive correctly. A faulty sender may omit a message, and that omission is detectable. Arbitrary loss or indefinite delays between loyal participants are outside this model.
- **Fixed membership:** IDs are `0..N-1`; the callable procedure validates membership size, commander, order, transport, and recursion depth.
- **Fault budget:** Actual faulty behavior is supplied by the transport, not discovered by the protocol. Violating `N >= 3m + 1` or exceeding m faults removes the guarantee; it does not make the inputs unexecutable.
- **Memory-only simulation:** No sockets, persistent storage, signatures, retries, duplicate-message buffers, timers, or recovery.
- **One commander's order:** No leader election, PBFT prepare/commit phases, client acknowledgments, replicated log, blockchain, or application-state machine.
- **Symbolic default:** `RETREAT` is a deterministic algorithm default, not a universal recommendation for a real robot's failure response.

## Verification

Verified on this machine using `g++` with C++17, `-Wall -Wextra -Wpedantic -Werror`, and executable launch through CMD:

- All four demonstrations produced the output shown above.
- A separate temporary harness passed OM(0), majority/tie defaults, omissions, input validation, commander-ID mapping, and the outside-bound counterexample.
- **432 exhaustive four-node cases** covered each commander ID, each possible single faulty participant, both initial orders, and every combination of `ATTACK`, `RETREAT`, or omission on that participant's relevant outgoing messages. All satisfied agreement and loyal-commander validity.
- **232 seven-node OM(2) cases** covered every fault subset of size zero, one, or two, both initial orders, and four deterministic fault behaviors, including omissions and path-dependent lies. These are selected tests, not an exhaustive enumeration of every two-fault behavior.
- Message-count and path checks confirmed 9 distinct reports for OM(1) and 156 for OM(2), without counting the same sender/path twice.

The harness also compiled with `-O2 -DNDEBUG -D_GLIBCXX_ASSERTIONS`; its checks remain enabled under `NDEBUG`. These tests support the implementation, but do not replace the algorithm's proof or communication assumptions. The temporary harness is separate from the compact learning source.

## References

- [Lamport, Shostak, and Pease — The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf), Section 3: recursive oral-message algorithm.
- [Related study notes: Classical Solutions and PBFT](../../Distributed-Systems-Theorems-and-Data-Structures.md#classical-solutions-and-pbft).
