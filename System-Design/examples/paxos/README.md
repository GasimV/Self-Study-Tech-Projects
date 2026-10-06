# Basic Paxos in C++17

Agree on **one value**, step by step, even when an acceptor is unavailable or another proposer interrupts an attempt.

> This is a learning simulation, not a production distributed service. Three acceptors, two proposers, and a learner run inside one process. Every invocation starts a fresh Paxos instance.

## Table of Contents

- [DSA-Style Paxos Core](#dsa-style-paxos-core)
  - [Core State and Roles](#core-state-and-roles)
  - [Language-Neutral Pseudocode](#language-neutral-pseudocode)
  - [Compact C++ Example](#compact-c-example)
  - [Complexity Breakdown](#complexity-breakdown)
  - [Core Assumptions](#core-assumptions)
- [Build and Run](#build-and-run)
- [How the Code Maps to Paxos](#how-the-code-maps-to-paxos)
- [Illustrated Input and Output](#illustrated-input-and-output)
  - [Basic: Successful Agreement](#basic-successful-agreement)
  - [Preserve: A Later Proposer Cannot Replace the Decision](#preserve-a-later-proposer-cannot-replace-the-decision)
  - [One Down: A Majority Still Works](#one-down-a-majority-still-works)
  - [No Quorum: Too Few Available Acceptors](#no-quorum-too-few-available-acceptors)
  - [Preempted: A Higher Proposal Interrupts an Attempt](#preempted-a-higher-proposal-interrupts-an-attempt)
  - [Partial Accept: Accepted Is Not Yet Chosen](#partial-accept-accepted-is-not-yet-chosen)
- [Self-Tests](#self-tests)
- [Limits and Important Distinctions](#limits-and-important-distinctions)
- [References](#references)

## DSA-Style Paxos Core

Start with [paxos_dsa.cpp](paxos_dsa.cpp) for the short algorithm. Then use [paxos.cpp](paxos.cpp) for the detailed walkthrough, message interleavings, and self-tests. Both implement **Basic Paxos for one decision**.

### Core State and Roles

Each acceptor remembers:

| State | Meaning |
| --- | --- |
| `promised` | Highest proposal number it has promised; initially `NONE`. |
| `accepted` | Accepted `(number, value)` pair, if any; initially `NONE`. |
| `available` | Whether the simulation can obtain a reply from this acceptor. |

Roles and procedures are different: a **role** says *who does the work*; a **procedure** says *what work is performed*.

| Role | Procedure in the compact version |
| --- | --- |
| **Proposer** | `Propose` collects promises, selects a value, and requests acceptance. |
| **Acceptor** | `Prepare` and `Accept` handle requests and update the acceptor's state. |
| **Learner** | The final majority check inside `Propose` identifies the chosen value from acknowledgments. |

For $N$ **configured** acceptors, the required majority is:

$$
Q = \left\lfloor \frac{N}{2} \right\rfloor + 1
$$

Unavailable acceptors still count toward $N$. A failure does **not** reduce the required quorum.

### Language-Neutral Pseudocode

`NONE` means no stored proposal or no decision established by this attempt. Proposal numbers are globally unique for new attempts; the same number must never identify different proposals. Each loop visits distinct acceptors once.

```text
PREPARE(node, number):
    if not node.available:
        return (false, NONE)
    if node.promised != NONE and number < node.promised:
        return (false, NONE)

    node.promised = number
    return (true, node.accepted)

ACCEPT(node, number, value):
    if not node.available:
        return false
    if node.promised != NONE and number < node.promised:
        return false
    if node.accepted != NONE and node.accepted.number == number
       and node.accepted.value != value:
        return false

    node.promised = number
    node.accepted = (number, value)
    return true

PROPOSE(nodes, number, requestedValue):
    quorum = floor(length(nodes) / 2) + 1
    promises = 0
    highestAccepted = NONE

    for each node in nodes:
        (ok, previous) = PREPARE(node, number)
        if not ok:
            continue
        promises = promises + 1
        if previous != NONE and
           (highestAccepted == NONE or previous.number > highestAccepted.number):
            highestAccepted = previous

    if promises < quorum:
        return NONE

    value = requestedValue
    if highestAccepted != NONE:
        value = highestAccepted.value

    acknowledgments = 0
    for each node in nodes:
        if ACCEPT(node, number, value):
            acknowledgments = acknowledgments + 1

    if acknowledgments < quorum:
        return NONE
    return value
```

**Why these steps matter:**

- **Promise:** lower-numbered attempts cannot override a newer promise.
- **Select:** preserve the highest accepted value reported by the promise quorum, even if it was not yet chosen.
- **Accept:** a promise quorum alone does not choose a value; a majority must actually accept the same proposal.

The C++ version returns `std::optional<int>`: a present value means majority acceptance was established, while `std::nullopt` corresponds to `NONE`. An integer such as `0` is a valid value, not a failure marker.

### Compact C++ Example

From the **repository root**:

```powershell
.\examples\paxos\build.cmd dsa
.\examples\paxos\paxos_dsa.exe
```

The build script creates `examples/paxos/paxos_dsa.exe`. Its no-argument behavior still builds the full walkthrough as `paxos.exe`.

Direct compilation is also possible:

```powershell
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/paxos/paxos_dsa.cpp -o examples/paxos/paxos_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/paxos/paxos_dsa.cpp -o examples/paxos/paxos_dsa
./examples/paxos/paxos_dsa
```

**Output:**

```text
Proposal 1 requests 20 -> chosen 20
Proposal 2 requests 5 -> chosen 20
```

**Financial interpretation:** Two proposals compete for the **same account-balance decision**: the first requests $20 and the second requests $5. After $20 is chosen, the second proposal discovers the earlier acceptance and must carry $20 forward. A larger proposal number is not permission to replace the decision.

> These are not two deposits. Separate deposits must both be processed through separate decisions. Paxos ensures agreement; application rules determine whether the amount is correct.

### Complexity Breakdown

Let $N$ be the number of configured acceptors. Assume proposal numbers and values have constant size.

| Measure | Complexity | Reason |
| --- | --- | --- |
| `Prepare` or `Accept` handler | O(1) time and state | A few comparisons and fixed-size state updates. |
| One `Propose` attempt | O(N) local work | At most two scans over the acceptors. |
| Proposer auxiliary space | O(1) | Counters and one highest accepted proposal; no reply collection. |
| Total acceptor state | O(N) | Constant-size state for each acceptor. |
| Equivalent broadcast message count | O(N) per attempt | Up to $N$ requests and $N$ replies in each of two phases: up to $4N$ messages, excluding separate learner notifications. |

An uncontended successful network implementation can use **two request/reply phases**: prepare/promise, then accept/acknowledge. Requests within a phase can be sent concurrently; a majority of successful replies is enough.

> **O(N) work is not a wall-clock latency guarantee.** This C++ version uses synchronous local calls, not network messages. Real message delays can be arbitrarily long, and competing proposers or failures can force retries. With $R$ attempts, local work and message count are O(RN); there is no fixed worst-case bound on $R$ or completion time in that setting.

### Core Assumptions

- **One decision, fixed membership:** the vector contains distinct acceptors; every new proposal concerns the same decision.
- **Unique proposal numbers:** callers supply a fresh globally unique number for each new attempt. The example uses `1` and `2`; it does not generate numbers for multiple independent processes.
- **Correct participants:** no Byzantine behavior or forged responses. An acceptor's reuse check does not replace the global uniqueness requirement.
- **Memory-only state:** no crash recovery. Real acceptors must persist promises and accepted proposals before replying.
- **Synchronous delivery:** no threads, real network transport, duplicate-message delivery, scheduling, or automatic retries. Each acceptor is called once per phase, so acknowledgments cannot be counted twice.
- **Learning is folded in:** successful `Accept` calls immediately supply acknowledgments. The compact version does not model a lost reply after an acceptance or a separately running learner.

> Returning `NONE` / `std::nullopt` means this attempt did not establish a decision. It does not prove that no earlier value was chosen. A failed attempt may also leave promises or individual acceptances behind; they must not be erased merely because a quorum was missing.

## Build and Run

From the **repository root**, with a C++17 compiler on your `PATH`:

```powershell
.\examples\paxos\build.cmd
.\examples\paxos\paxos.exe --scenario basic
.\examples\paxos\paxos.exe --self-test
```

The [Windows build script](build.cmd) creates `examples/paxos/paxos.exe` by default. It locates the source and output relative to the script itself, not your current directory. It works from PowerShell or Command Prompt without changing PowerShell's execution policy. From inside `examples/paxos`, you can also run `.\build.cmd` and then `.\paxos.exe --scenario basic`.

To compile directly without the script, use the same output path explicitly:

```powershell
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/paxos/paxos.cpp -o examples/paxos/paxos.exe
```

Linux/macOS equivalent:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/paxos/paxos.cpp -o examples/paxos/paxos
./examples/paxos/paxos --scenario basic
./examples/paxos/paxos --self-test
```

No external libraries or build system are required. The generated executables are ignored by the local `.gitignore`, so they are not committed. A previously generated root-level `paxos.exe` is not moved or removed by this script.

The CLI arguments are the **input**; the message trace, decision, and final acceptor table are the **output**. Values and message delivery are scripted, so results are reproducible.

| Input | What it illustrates | Expected outcome |
| --- | --- | --- |
| `--scenario basic` | All acceptors reply. | Choose `book r1 for u1`. |
| `--scenario preserve` | P2 proposes a different value after P1's decision. | Preserve `book r1 for u1`. |
| `--scenario one-down` | A3 is unavailable. | A1 and A2 still choose `book r1 for u1`. |
| `--scenario no-quorum` | A2 and A3 are unavailable. | Stop before accept: only one promise. |
| `--scenario preempted` | P2 prepares a higher proposal before P1's accept. | Reject P1's accept; P2 chooses `book r1 for u2`. |
| `--scenario partial-accept` | Only A1 initially accepts P1's value. | P2 observes and carries that value forward, then chooses it. |
| `--self-test` | Run protocol and scenario checks. | Print `ALL TESTS PASSED`. |
| `--help` | Show arguments and scenario names. | Print usage. |

Successful scenarios, including the deliberate no-quorum scenario, exit with code `0`. Invalid arguments, unknown scenarios, or failing self-tests exit with code `1`.

## How the Code Maps to Paxos

Read [paxos.cpp](paxos.cpp) in this order:

| Component | What to look for |
| --- | --- |
| `ProposalId` | `(counter, proposer ID)`, compared lexicographically: `(1,P1) < (1,P2) < (2,P1)`. |
| `Acceptor::onPrepare` | Promise not to accept lower proposals; report the highest previously accepted proposal. |
| `Proposer::onPromise` and `selectValue` | Count distinct promises; adopt the highest accepted value in those replies, or use the requested value if none exists. |
| `Acceptor::onAccept` | Accept unless a higher promise blocks the request; record the acceptance before replying. |
| `Learner::onAccepted` | Count distinct acceptors that accepted the same proposal ID **and value**. Learn after a majority. |
| `Simulation` and `runScenario` | Deliver requests explicitly, skip unavailable nodes, and interleave competing attempts. |
| `selfTest` | Check scenarios and safety-related behavior with always-active assertions. |

For three configured acceptors:

$$
Q = \left\lfloor \frac{3}{2} \right\rfloor + 1 = 2
$$

**The quorum stays two when a node fails.** Reducing it to a majority of only the currently available nodes could allow isolated groups to choose conflicting values.

The acceptor stores:

- **Highest promise:** the smallest proposal ID it will still accept; lower IDs are rejected.
- **Accepted proposal:** its most recently accepted proposal ID and value, if any.

The proposer keeps the selected value fixed for its proposal ID. Duplicate promises and acknowledgments are safe to replay but count only once. Replies from previous attempts or acceptors outside the configured group do not count toward a new quorum.

> **Accepted:** one acceptor recorded a proposal. **Chosen:** a majority accepted the same proposal. **Learned:** a learner received enough acknowledgments to know the value was chosen. A value may be chosen even before the learner receives all the evidence.

The following outputs are taken from the program. Blocks labeled **excerpt** omit other parts of that scenario's trace.

## Illustrated Input and Output

### Basic: Successful Agreement

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario basic
```

**Output:**

```text
SCENARIO: basic
ACCEPTORS: A1, A2, A3
MAJORITY: 2

INPUT: P1 proposes "book r1 for u1"
PREPARE (1,P1)
  A1: PROMISE; no previously accepted value
  A2: PROMISE; no previously accepted value
  A3: PROMISE; no previously accepted value
PROMISES: 3/3; 2 required.
SELECT: "book r1 for u1"
REASON: No prior acceptance in the promise quorum; use the requested value.
ACCEPT (1,P1), "book r1 for u1"
  A1: ACCEPTED
  A2: ACCEPTED
  A3: ACCEPTED
ACKNOWLEDGMENTS: 3/3; 2 required.
RESULT: CHOSEN "book r1 for u1"
LEARNER: matching majority evidence received; decision learned.

FINAL ACCEPTOR STATE
Node | Available | Highest promise | Accepted proposal | Accepted value
A1   | yes | (1,P1) | (1,P1) | "book r1 for u1"
A2   | yes | (1,P1) | (1,P1) | "book r1 for u1"
A3   | yes | (1,P1) | (1,P1) | "book r1 for u1"
LEARNED VALUE: "book r1 for u1"
```

**Recall:** Two acknowledgments would have been enough. This scenario delivers to all three for visibility; it does not require unanimity.

### Preserve: A Later Proposer Cannot Replace the Decision

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario preserve
```

P1 first chooses `book r1 for u1`. P2 then requests `book r1 for u2` using a higher proposal ID.

**Output excerpt — P2's attempt and final state:**

```text
INPUT: P2 proposes "book r1 for u2"
PREPARE (2,P2)
  A1: PROMISE; previously accepted (1,P1), "book r1 for u1"
  A2: PROMISE; previously accepted (1,P1), "book r1 for u1"
  A3: PROMISE; previously accepted (1,P1), "book r1 for u1"
PROMISES: 3/3; 2 required.
SELECT: "book r1 for u1"
REASON: Preserve the highest accepted value in the promise quorum.
P2's requested value was not selected.
ACCEPT (2,P2), "book r1 for u1"
  A1: ACCEPTED
  A2: ACCEPTED
  A3: ACCEPTED
ACKNOWLEDGMENTS: 3/3; 2 required.
RESULT: CHOSEN "book r1 for u1"
LEARNER: matching majority evidence received; decision learned.

FINAL ACCEPTOR STATE
Node | Available | Highest promise | Accepted proposal | Accepted value
A1   | yes | (2,P2) | (2,P2) | "book r1 for u1"
A2   | yes | (2,P2) | (2,P2) | "book r1 for u1"
A3   | yes | (2,P2) | (2,P2) | "book r1 for u1"
LEARNED VALUE: "book r1 for u1"
```

**Recall:** A higher proposal ID is a newer *attempt*, not permission to change an already chosen value. Multiple proposal IDs may be chosen, but their value must stay the same for this single decision.

### One Down: A Majority Still Works

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario one-down
```

A3 receives no requests; A1 and A2 provide both the promise quorum and acceptance quorum.

**Output excerpt — accept phase:**

```text
ACCEPT (1,P1), "book r1 for u1"
  A1: ACCEPTED
  A2: ACCEPTED
  A3: UNAVAILABLE (no reply)
ACKNOWLEDGMENTS: 2/3; 2 required.
RESULT: CHOSEN "book r1 for u1"
LEARNER: matching majority evidence received; decision learned.
```

**Recall:** A3 does not need to accept for the value to be chosen. A lagging acceptor is not itself evidence of a conflicting decision.

### No Quorum: Too Few Available Acceptors

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario no-quorum
```

**Output:**

```text
SCENARIO: no-quorum
ACCEPTORS: A1, A2, A3
MAJORITY: 2
UNAVAILABLE: A2, A3

INPUT: P1 proposes "book r1 for u1"
PREPARE (1,P1)
  A1: PROMISE; no previously accepted value
  A2: UNAVAILABLE (no reply)
  A3: UNAVAILABLE (no reply)
PROMISES: 1/3; 2 required.
RESULT: NO QUORUM - this attempt cannot enter the accept phase.

FINAL ACCEPTOR STATE
Node | Available | Highest promise | Accepted proposal | Accepted value
A1   | yes | (1,P1) | none | none
A2   | no | none | none | none
A3   | no | none | none | none
LEARNED VALUE: none (absence of learning is not proof of absence of a decision)
```

**Recall:** This fresh instance makes no decision. In general, a failed attempt does not prove that an earlier attempt also failed or that no decision exists elsewhere. Paxos preserves safety when progress stops.

### Preempted: A Higher Proposal Interrupts an Attempt

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario preempted
```

1. P1 obtains promises for `(1,P1)` but has not sent accept requests.
2. P2 obtains higher promises for `(2,P2)`.
3. Acceptors reject P1's delayed accept requests.
4. P2's accept requests succeed.

**Output excerpt — the two accept phases:**

```text
ACCEPT (1,P1), "book r1 for u1"
  A1: REJECTED; promised (2,P2)
  A2: REJECTED; promised (2,P2)
  A3: REJECTED; promised (2,P2)
ACKNOWLEDGMENTS: 0/3; 2 required.
RESULT: NO QUORUM - no decision learned from this attempt's replies.
This does not prove that no earlier or unobserved decision exists.
ACCEPT (2,P2), "book r1 for u2"
  A1: ACCEPTED
  A2: ACCEPTED
  A3: ACCEPTED
ACKNOWLEDGMENTS: 3/3; 2 required.
RESULT: CHOSEN "book r1 for u2"
LEARNER: matching majority evidence received; decision learned.
```

**Recall:** P1's promises did not reserve the decision forever. P2 can choose its requested value here because no previous value had been accepted when it collected promises.

### Partial Accept: Accepted Is Not Yet Chosen

**Input:**

```powershell
.\examples\paxos\paxos.exe --scenario partial-accept
```

P1 obtains a promise quorum, but its accept request reaches only A1. That is **one acceptance**, not a majority decision.

**Output excerpt — partial delivery:**

```text
DELIVERY: Only A1 receives this ACCEPT request.
ACCEPT (1,P1), "book r1 for u1"
  A1: ACCEPTED
ACKNOWLEDGMENTS: 1/3; 2 required.
RESULT: NO QUORUM - no decision learned from this attempt's replies.
This does not prove that no earlier or unobserved decision exists.

A1 accepted, but one acceptance is not a chosen value.
P2's promise quorum includes A1, so P2 must carry its value forward.
```

**Output excerpt — P2 discovers A1's acceptance:**

```text
INPUT: P2 proposes "book r1 for u2"
PREPARE (2,P2)
  A1: PROMISE; previously accepted (1,P1), "book r1 for u1"
  A2: PROMISE; no previously accepted value
  A3: PROMISE; no previously accepted value
PROMISES: 3/3; 2 required.
SELECT: "book r1 for u1"
REASON: Preserve the highest accepted value in the promise quorum.
P2's requested value was not selected.
```

P2 then obtains three acceptances for `(2,P2)`, choosing `book r1 for u1`.

**Recall:** A proposer follows the highest-accepted-value rule even when that value was not yet chosen. It cannot infer from individual promise replies whether a previous proposer obtained a majority. If P2 had used only A2 and A3 as its promise quorum here, neither would report P1's acceptance, and selecting P2's own value would be allowed.

## Self-Tests

```powershell
.\examples\paxos\paxos.exe --self-test
```

Assertions remain active even when compiled with `-DNDEBUG`.

The checks cover:

- All six scenarios and their expected decisions.
- Fixed majority size despite unavailable nodes; failed prepare does not enter accept.
- Duplicate prepare/accept requests and replies; distinct acceptors are counted once.
- Nonmember responses and stale promise replies do not contribute to a quorum.
- Rejection of lower proposal IDs and detection of conflicting ID reuse.
- Correct lexicographic ordering, including equal counters from different proposers.
- Selection of the **highest accepted proposal**, not the first reply received.
- An immutable value after a proposal's selection and preservation across later attempts.
- Failures between phases, retries after availability returns, and preservation across different quorums.
- A value chosen by acceptors but not yet learned when its second acknowledgment is delayed.

The final line is:

```text
ALL TESTS PASSED
```

These tests exercise important rules; they are not a formal proof or an exhaustive exploration of every asynchronous execution.

## Limits and Important Distinctions

- **Single decision:** All attempts in one run concern the same decision. Agreeing on many commands requires multiple instances or Multi-Paxos, which this example does not implement.
- **One process:** Handler calls stand in for messages. Delivery order is controlled explicitly; there are no sockets, threads, real clocks, or automatic retries.
- **Memory only:** Unavailable nodes keep their objects and state. Restarting the program discards the entire instance. Real crash recovery requires durable promises and accepted proposals before acknowledgments, plus unique proposal IDs across proposer restarts.
- **Fixed membership:** There are always three configured acceptors and a quorum of two. There is no membership-change protocol.
- **Correct participants:** The learner trusts replies generated by acceptor handlers. The example does not handle forged messages or Byzantine behavior.
- **Learning may lag:** A lost acknowledgment does not undo an acceptance. Lack of majority evidence at the learner does not mean a value was never chosen.
- **Progress is not guaranteed under endless interference:** Competing proposers may repeatedly preempt each other. A stable leader helps practical deployments progress.
- **Not a booking service:** The value is an illustrative command string. The simulation does not execute reservations, validate room availability, or deduplicate client retries. Consensus is a building block, not the whole application.

## References

- [Paxos study notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#paxos)
- [Leslie Lamport — Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
