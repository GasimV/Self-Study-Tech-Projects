# Distributed Systems Theorems and Data Structures

## Table of Contents

- [Overview](#overview)
- [CAP Theorem](#cap-theorem)
  - [The Three Properties](#the-three-properties)
  - [CAP Diagram](#cap-diagram)
  - [Why a Partition Forces a Choice](#why-a-partition-forces-a-choice)
  - [CP, AP, and CA](#cp-ap-and-ca)
  - [Practical Design Notes](#practical-design-notes)
- [PACELC Theorem](#pacelc-theorem)
  - [What PACELC Stands For](#what-pacelc-stands-for)
  - [PACELC Diagram](#pacelc-diagram)
  - [The Two Trade-Offs](#the-two-trade-offs)
- [Consensus and Replication Protocols](#consensus-and-replication-protocols)
  - [Consensus and Majority Quorums](#consensus-and-majority-quorums)
  - [Paxos](#paxos)
    - [Paxos Roles](#paxos-roles)
    - [Paxos Protocol Steps](#paxos-protocol-steps)
    - [Paxos Protocol Diagram](#paxos-protocol-diagram)
    - [Paxos Walkthrough: Two Competing Values](#paxos-walkthrough-two-competing-values)
    - [Paxos Challenges](#paxos-challenges)
    - [Paxos Variants and Optimizations](#paxos-variants-and-optimizations)
    - [Paxos Applications](#paxos-applications)
  - [Raft](#raft)
    - [Raft Roles and Terms](#raft-roles-and-terms)
    - [Raft State Diagram](#raft-state-diagram)
    - [Raft Protocol Steps](#raft-protocol-steps)
    - [Raft Safety Rules](#raft-safety-rules)
    - [Raft Challenges](#raft-challenges)
    - [Raft Applications](#raft-applications)
    - [Named Systems and Algorithm Boundaries](#named-systems-and-algorithm-boundaries)
  - [Zab and ZooKeeper](#zab-and-zookeeper)
  - [Other Protocols to Study Later](#other-protocols-to-study-later)
  - [Paxos vs. Raft vs. Zab](#paxos-vs-raft-vs-zab)
- [Byzantine Generals Problem (BGP)](#byzantine-generals-problem-bgp)
  - [The Generals Example](#the-generals-example)
  - [Requirements for Byzantine Agreement](#requirements-for-byzantine-agreement)
  - [Byzantine Faults vs. Crash Faults](#byzantine-faults-vs-crash-faults)
  - [Byzantine Fault Tolerance and Quorums](#byzantine-fault-tolerance-and-quorums)
  - [Common BFT Techniques](#common-bft-techniques)
  - [Classical Solutions and PBFT](#classical-solutions-and-pbft)
  - [When Is BFT Needed?](#when-is-bft-needed)
  - [BFT Applications and Trade-Offs](#bft-applications-and-trade-offs)
  - [BFT and AI/LLM-Based Systems](#bft-and-aillm-based-systems)
- [FLP Impossibility Theorem](#flp-impossibility-theorem)
  - [Consensus Requirements](#consensus-requirements)
  - [FLP Assumptions](#flp-assumptions)
  - [FLP Impossibility Triangle](#flp-impossibility-triangle)
  - [Why a Slow Node Looks Like a Failed Node](#why-a-slow-node-looks-like-a-failed-node)
  - [What FLP Does and Does Not Say](#what-flp-does-and-does-not-say)
  - [How Practical Systems Make Progress](#how-practical-systems-make-progress)
  - [Kafka Example: FLP and KRaft](#kafka-example-flp-and-kraft)
  - [FLP vs. CAP](#flp-vs-cap)
- [Consistent Hashing](#consistent-hashing)
  - [Why Modulo Hashing Causes Reorganization](#why-modulo-hashing-causes-reorganization)
  - [How the Hash Ring Works](#how-the-hash-ring-works)
  - [Simple Ring Example](#simple-ring-example)
  - [Adding or Removing a Server](#adding-or-removing-a-server)
  - [Problems with One Token per Server](#problems-with-one-token-per-server)
  - [Virtual Nodes: Multiple Tokens per Server](#virtual-nodes-multiple-tokens-per-server)
  - [Enhanced Ring Diagram](#enhanced-ring-diagram)
  - [Applications and Practical Limits](#applications-and-practical-limits)
- [Bloom Filters](#bloom-filters)
  - [How a Bloom Filter Works](#how-a-bloom-filter-works)
  - [Membership Guarantees](#membership-guarantees)
  - [Username Example](#username-example)
  - [Membership Decision Diagram](#membership-decision-diagram)
  - [Sizing and False-Positive Trade-Offs](#sizing-and-false-positive-trade-offs)
  - [Bloom Filter Applications](#bloom-filter-applications)
  - [Limitations and Safe Use](#limitations-and-safe-use)
  - [DSA-Style Bloom Filter Implementation](#dsa-style-bloom-filter-implementation)
- [Count-Min Sketch](#count-min-sketch)
- [HyperLogLog](#hyperloglog)
- [References](#references)

## Overview

Distributed systems need more than additional servers. Nodes must communicate, coordinate updates, handle failures, and manage large datasets.

These topics explain what distributed systems can guarantee and how to build within those limits:

| Category | Topics | Main question |
| --- | --- | --- |
| Theorems and trade-off models | CAP, PACELC, FLP | Which guarantees are possible under the stated conditions? |
| Consensus and replication protocols | Paxos, Raft, Zab | How can nodes agree on decisions or an ordered sequence of updates? |
| Fault models and agreement problems | Byzantine generals problem | How can nodes agree when some participants behave incorrectly? |
| Data distribution and compact summaries | Consistent hashing, Bloom filters, Count-Min Sketch, HyperLogLog | How can we distribute data or answer questions with limited memory? |

See [Distributed System Attributes](Distributed-System-Attributes.md) for the underlying concepts of consistency, availability, partition tolerance, and fault tolerance.

## CAP Theorem

The **CAP theorem**, also called *Brewer's theorem*, states that a distributed read/write system cannot guarantee both **strong consistency** and **availability** during a **network partition**.

> **Remember:** When nodes cannot communicate, the system cannot always provide both an up-to-date answer and an answer to every request.

### The Three Properties

| Property | Plain meaning | Hotel-room example |
| --- | --- | --- |
| **C — Consistency** | Operations behave as if there were one up-to-date copy of the data. A read after a completed write sees that write or a newer one. | After a booking completes, a later availability read cannot report the room as still free. |
| **A — Availability** | Every request reaching a non-failing node eventually completes its requested operation, even if other nodes cannot be reached. | A reachable replica continues answering availability checks rather than refusing them because it cannot contact another replica. |
| **P — Partition tolerance** | The design handles network splits that prevent groups of nodes from communicating. | `db1` and `db2` remain running, but their network connection is broken. |

Here, **consistency means linearizability**. CAP availability is a formal guarantee about completing requests; it does not specify a response deadline or an uptime percentage. Production systems also need latency and availability targets. [Gilbert and Lynch's explanation](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf)

### CAP Diagram

> **During a network partition, a system cannot guarantee both strong consistency and availability. CA is possible when there is no partition; if one occurs, the system must give up at least one of those guarantees.**

```mermaid
flowchart TB
    CA["CA<br/>Consistency + Availability<br/>No partition guarantee"]
    C(("Consistency<br/>C"))
    A(("Availability<br/>A"))
    CP["CP<br/>Preserve consistency<br/>Some requests cannot complete"]
    AP["AP<br/>Keep serving requests<br/>Data may be stale or conflicting"]
    P(("Partition<br/>Tolerance<br/>P"))

    CA --- C
    CA --- A
    C --- CP
    A --- AP
    CP --- P
    AP --- P

    classDef property fill:#fff,stroke:#111,stroke-width:2px,color:#111
    classDef ca fill:#fff,stroke:#d32f2f,stroke-width:2px,color:#d32f2f
    classDef cp fill:#fff,stroke:#008000,stroke-width:2px,color:#008000
    classDef ap fill:#fff,stroke:#0000ff,stroke-width:2px,color:#0000ff
    class C,A,P property
    class CA ca
    class CP cp
    class AP ap
```

> **Diagram:** The circles represent the three properties; the connecting boxes show the familiar CA, CP, and AP combinations. During a partition, the relevant choice is **CP or AP**. CA assumes partitions are excluded; it cannot preserve both guarantees if a partition occurs.

### Why a Partition Forces a Choice

**Hotel-room example:**

1. `u1` books room `r1` on `db1`, and the booking is confirmed.
2. A network partition prevents the update from reaching `db2`.
3. `u2` asks `db2` whether `r1` is available. `db2` still has the old value and cannot check `db1`.
4. If `db2` answers from its local copy, it may return **“available”** despite the completed booking. If it waits for communication to return, the request cannot complete while the partition persists.

> The isolated replica cannot know whether its data is current. Answering risks breaking consistency; waiting sacrifices availability.

### CP, AP, and CA

| Choice | Behavior during a partition | Example |
| --- | --- | --- |
| **CP — Consistency + partition tolerance** | Preserve strong consistency, even if some reads or writes must wait or fail. | An isolated replica refuses to confirm a booking it cannot safely coordinate. |
| **AP — Availability + partition tolerance** | Continue serving requests, accepting weaker consistency and possible conflicting updates. | Hotel search returns locally stored availability that may be outdated. |
| **CA — Consistency + availability** | Can provide both when partitions are excluded from the assumed failure conditions. | Normal operation with reliable communication; a partition would still force a C/A decision. |

### Practical Design Notes

- **Plan for partitions:** Hardware faults, network outages, routing problems, and maintenance can break communication, even within one region.
- **CP does not mean every replica is always identical:** Some replicas can lag; the system must prevent those copies from serving inconsistent operations.
- **CP does not mean the whole service stops:** A group with enough reachable replicas may continue while an isolated group cannot.
- **AP does not automatically mean eventual consistency:** Convergence also requires replication and conflict-resolution rules.
- **Choose per operation:** Search can tolerate stale room availability, while final booking confirmation needs stronger coordination and an atomic check-and-write.

> **CAP describes a limit during partitions, rather than a rule to permanently abandon one property.** Define which operations can continue, which must wait, and how conflicting updates will be handled when communication returns. *CAP prohibits only a tiny part of the design space: ***perfect availability and consistency*** in the presence of partitions, which are ***rare***.* [Eric Brewer's clarification](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)

> **CAP does not mean sacrificing consistency or availability in every situation.** When communication works normally, a system can provide both. During a partition, designers must decide which guarantee to prioritize for the affected operations.
> - ***For financial transactions***, where strict consistency is essential, a CP approach may be preferred: some requests must wait or fail rather than use inconsistent data. ***For web features*** such as feeds, an AP approach may be preferred: users continue receiving responses, even if some information is temporarily outdated.
> - ***The design choice*** depends on the specific/unique system requirements and priorities of an application, user needs, and expected network conditions. Different operations within the same system can make different choices. CAP helps system architects make ***conscious*** decisions about which operations can continue during a partition and how to recover afterward.

## PACELC Theorem

**PACELC** extends CAP by considering what happens both **during a network partition** and **during normal operation**. It was introduced by Daniel Abadi.

> **Remember:** If there is a **P**artition, consider **A**vailability versus **C**onsistency; **E**lse, consider **L**atency versus **C**onsistency.

### What PACELC Stands For

| Letter | Meaning | Plain explanation |
| --- | --- | --- |
| **P** | Partition | Some groups of nodes cannot communicate. The design must decide which operations can continue. |
| **A** | Availability | Requests reaching healthy nodes continue to receive results, even if strong consistency cannot be maintained. |
| **C** | Consistency during a partition | Preserve strong consistency, even if some operations must wait or fail. |
| **E** | Else | There is no network partition; the system is operating normally. |
| **L** | Latency | Reduce the time between sending a request and receiving its result. |
| **C** | Consistency during normal operation | Keep strong consistency, accepting the communication and coordination time it may require. |

Both **C** letters concern consistency. They describe priorities under different network conditions, rather than two separate definitions of consistency.

### PACELC Diagram

```mermaid
flowchart TB
    P{"Is there a network<br/>partition?"}
    P -->|Yes| DURING("Choose a priority<br/>during the partition")
    P -->|No| NORMAL("Choose a priority<br/>during normal operation")
    DURING --> A("Availability")
    DURING --> CP("Consistency")
    NORMAL --> L("Low latency")
    NORMAL --> CE("Consistency")

    classDef decision fill:#fff,stroke:#111,stroke-width:2px,color:#111
    classDef choice fill:#ffffcc,stroke:#111,stroke-width:2px,color:#111
    classDef availability fill:#bdbdbd,stroke:#111,stroke-width:2px,color:#111
    classDef latency fill:#d3c5c5,stroke:#111,stroke-width:2px,color:#111
    class P,CP,CE decision
    class DURING,NORMAL choice
    class A availability
    class L latency
```

**Diagram:** The left branch is the CAP trade-off: **availability versus consistency during a partition**. The right branch adds the PACELC trade-off: **latency versus consistency when there is no partition**.

### The Two Trade-Offs

- **During a partition — availability vs. consistency:** A replica can answer from its local data, which may be outdated, or refuse an operation it cannot safely coordinate.
- **During normal operation — latency vs. consistency:** Waiting for other replicas to coordinate an update takes time. Responding before that coordination completes can reduce latency, but another replica may return an older value.

**Hotel-room example:** *During a partition*, hotel search may return locally stored room availability, while final booking confirmation may have to wait. *Even when the network works*, confirming a booking through coordinated replicas takes longer than returning an uncoordinated local result.

**Common notation:** `PA/EL` prioritizes availability during partitions and low latency otherwise; `PC/EC` prioritizes consistency in both situations. These labels describe a design or configuration, not an unchangeable property of every operation in a product.

> CAP explains the partition-time limit. PACELC also asks what consistency costs in response time during normal operation. Choose according to the application's requirements, replica locations, and acceptable data staleness. [Abadi's original explanation](https://dbmsmusings.blogspot.com/2010/04/problems-with-cap-and-yahoos-little.html), [PACELC paper](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)

## Consensus and Replication Protocols

**Consensus** means that participating nodes agree on a decision. Replicated services use consensus repeatedly to agree on an **ordered sequence of commands**, so replicas can apply the same commands and reach the same state.

**Example:** A booking service must agree on which request reserves the final room. Agreeing on command order lets every replica perform the same availability check and reach the same booking result.

### Consensus and Majority Quorums

Standard Paxos and Raft handle **crashes, unavailable nodes, and delayed or lost messages**. They assume participants follow the protocol; they do not provide Byzantine fault tolerance against dishonest or arbitrarily incorrect participants.

For $N$ voting nodes, a majority quorum is:

$$
Q = \left\lfloor \frac{N}{2} \right\rfloor + 1
$$

| Voting nodes | Majority needed | Unavailable nodes tolerated while retaining a majority |
| ---: | ---: | ---: |
| 3 | 2 | 1 |
| 5 | 3 | 2 |
| 7 | 4 | 3 |

To tolerate $f$ unavailable voting nodes, a typical majority-based deployment needs at least $2f + 1$ voters. The remaining majority must be able to communicate.

> **Safety vs. progress:** Safety prevents conflicting decisions. Progress means new decisions can be made. A partition can stop progress without allowing the protocol to make conflicting decisions. Progress requires a reachable quorum and sufficiently stable communication and leadership.

### Paxos

**Paxos**, developed by **Leslie Lamport**, allows nodes to agree on **one value for one decision**, even when some nodes fail or messages are delayed. A value can be a command, a proposed update, or another decision the replicas must share.

> **Financial example:** Two nodes propose different values for the **same account-balance update**: Node 1 proposes **$20**, while Node 2 proposes **$5**. Paxos ensures that only one value is chosen for that decision. If **$20** is chosen, a later proposal cannot choose **$5** for the same decision.

> Paxos ensures agreement—not that the amount is financially correct. If $20 and $5 represent **two separate deposits**, both must be processed through separate decisions, rather than choosing one and discarding the other.

**Basic Paxos** chooses a single value; **Multi-Paxos** repeats agreement for positions in an ordered log. These decisions are building blocks for databases, storage systems, and replicated state machines.

**Hands-on example:** [C++17 Basic Paxos simulation](examples/paxos/README.md) — step-by-step input/output, competing proposals, unavailable acceptors, and self-tests. [Implementation](examples/paxos/paxos.cpp).

#### Paxos Roles

| Role | Responsibility |
| --- | --- |
| **Proposer** | Suggests a value and coordinates the prepare and accept phases. |
| **Acceptor** | Records promises and accepted proposals; a quorum of acceptors determines which value is chosen. |
| **Learner** | Finds out which value was chosen and passes it to the application. |

These are **logical roles**: one server can perform more than one role.

A proposal contains a **unique, ordered proposal number** $n$ and a **value** $v$. Proposal numbers let acceptors distinguish newer attempts from older ones; they can be constructed from a counter and proposer ID.

#### Paxos Protocol Steps

1. **Prepare:** The proposer selects a proposal number $n$ and sends `Prepare(n)` to acceptors, seeking a majority of responses.
2. **Promise:** An acceptor that has not promised a higher or equal number promises not to accept proposals numbered below $n$. It returns its **highest-numbered previously accepted proposal**, if any. Older attempts may be rejected or ignored.
3. **Select the value:** After a majority of promises, the proposer must use the value from the **highest-numbered accepted proposal in those replies**. If none of the responding acceptors has accepted a value, it may use its own proposed value.
4. **Accept:** The proposer sends `Accept(n, v)`. An acceptor accepts unless it has since promised a higher proposal number, and records the accepted proposal before acknowledging it.
5. **Learn:** Once a majority accepts the same proposal, its value is **chosen**. Learners obtain evidence of that decision and inform the application.

> **Critical rule:** A new proposer cannot simply overwrite an earlier accepted value with its preferred value. Carrying forward the highest-numbered accepted value from the promise quorum preserves earlier decisions. **Accepted by one node** is different from **chosen by a majority**. [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)

**Proposal number vs. proposed value**

- **Higher/lower** means a larger/smaller **proposal number**, not a larger/smaller money amount.
- In this example, **#2 is newer and higher-numbered** than #1, even if #2 initially requests **$5** and #1 requests **$20**.
- The **proposal number** identifies the attempt. The **value** is what that attempt proposes for the decision.

**What does a promise actually say?**

Suppose an acceptor previously accepted `(#1, $20)`. When it receives `Prepare(2)`, it replies with **two separate pieces of information**:

> **Promise:** "From now on, I will not accept proposals numbered below #2."
>
> **History:** "I previously accepted (#1, $20)."

The promise does **not** erase the earlier $20. The history lets the proposer check whether an earlier value must be preserved. If this is the highest-numbered accepted proposal in its promise quorum, the proposer must use $20.

"Highest-numbered previously accepted proposal" means **the accepted proposal with the largest proposal number**, not the largest money amount. For example, if a `Prepare(4)` quorum reports acceptances numbered #1 and #3, the proposer uses the value attached to **#3**.

**Proposal #2 does not become proposal #1**

Reporting `(#1, $20)` is **sharing history**, not renaming #2. The new attempt is still #2, and it may carry the same $20 value:

```text
Accept #1: $20  -> accepted earlier
Prepare #2     -> promise to refuse lower numbers; report earlier (#1, $20)
Accept #2: $20  -> allowed if no higher promise has intervened
Accept #1: $20  -> rejected if it arrives again after that promise to #2
```

It is the **late request carrying #1** that is rejected, not the new request carrying #2. Even the same $20 value does not make an old proposal number acceptable again.

**How can an older proposal physically arrive later?**

Different proposers send messages independently, and **network messages can be delayed**:

1. **P1 sends `Accept(1, $20)` to A, B, and C.** A and B receive and accept it, so $20 is chosen. The message to C is delayed in the network.
2. **P2 sends `Prepare(2)` to B and C.** These messages arrive quickly. B reports its earlier `(#1, $20)` acceptance, so P2 must carry $20 forward.
3. **P2 sends `Accept(2, $20)` to B and C.** Both accept it.
4. **P1's delayed `Accept(1, $20)` finally reaches C.** C replies: "Too late—I already promised #2. I reject #1."

Nothing changed #2 back into #1. **An old message simply arrived after a newer message.** A proposer can also retry the same request when a reply is delayed or lost, creating another late copy.

> **Proposal numbers describe proposal order—not network arrival order.** A higher-numbered request may arrive before a lower-numbered request.

**What if the acceptor has already promised another number?**

- Already promised **#3**, then receives `Prepare(2)`: **reject or ignore it**, because #2 is lower.
- Already promised **#2**, then receives `Prepare(2)` again: this is a **duplicate**, not a new proposal. An implementation may repeat its reply or ignore the duplicate; the C++ examples repeat the reply.
- Already promised **#2**, then receives `Prepare(3)`: it can make a **higher promise**. Promising #2 does not permanently forbid later attempts.

#### Paxos Protocol Diagram

```mermaid
sequenceDiagram
    participant P as Proposer
    participant A as Acceptor

    Note over P,A: Phase 1 - Prepare and promise
    P->>A: Prepare(n)
    alt n is greater than the promised number
        A-->>P: Promise(n, highest accepted proposal if any)
    else A has already promised an equal or higher number
        A-->>P: Ignore or reject the older attempt
    end

    Note over P: Gather a majority of promises<br/>Select v using the highest accepted proposal<br/>or use a new value if none was accepted

    Note over P,A: Phase 2 - Accept
    P->>A: Accept(n, v)
    alt A has not promised a number greater than n
        A-->>P: Accepted(n, v)
    else A has since promised a higher number
        A-->>P: Ignore or reject the accept request
    end

    Note over P,A: v is chosen only after a majority accepts<br/>Learners are then informed
```

**Diagram:** One proposer/acceptor exchange is shown, as in the protocol illustration. In a real group, the proposer exchanges these messages with multiple acceptors and needs a **majority**, not just one reply. Promise responses carry the highest accepted proposal for this decision, rather than a complete list of all proposals.

**Example:** If `db1` and `db2` accept proposal `(7, "book r1 for u1")` in a three-acceptor group, that value is chosen. A later proposer seeking a majority must preserve that decision, even if it originally wanted to propose another value.

#### Paxos Walkthrough: Two Competing Values

Think of Paxos as solving this exact question for **one decision / log slot**:

> **Three database nodes must agree: should this record contain $20 or $5?**

Assume three acceptors, **A, B, and C**, initially with no accepted proposal. A majority is **2 out of 3**. P1 and P2 are proposers; they may run on the same servers as the acceptors, but their roles are different.

> **Higher/lower and newer/older refer to the proposal number, not the money amount.** In this example, proposal **#2 is newer and higher-numbered**, even if its requested value is **$5**. Proposal **#1 is older and lower-numbered**, even if its value is **$20**. The **proposal number** and the **proposed value** are separate things.

**1. P1 gets $20 chosen**

P1 wants $20 and starts proposal **#1**. It sends `Prepare(1)` to A and B. Both reply:

```text
A: I promise not to accept proposals below #1. No earlier value accepted.
B: I promise not to accept proposals below #1. No earlier value accepted.
```

Because neither reply reports an earlier acceptance, P1 can use its requested value. It sends `Accept(1, $20)` to A and B, which record:

| Acceptor | Accepted proposal |
| --- | --- |
| A | `(#1, $20)` |
| B | `(#1, $20)` |
| C | None |

**Two of three acceptors accepted the same proposal, so $20 is now chosen.** C does not need to participate for that decision to be made.

**2. P2 wants $5, but must preserve $20**

P2 starts a newer proposal, **#2**, initially wanting $5. It sends `Prepare(2)` to B and C. Their replies contain both a promise and their accepted history:

```text
B: I promise not to accept proposals below #2. I already accepted (#1, $20).
C: I promise not to accept proposals below #2. No earlier value accepted.
```

The crucial rule is:

> P2 must reuse the value from the **highest-numbered accepted proposal in its promise quorum**. It cannot continue with $5 for this decision.

Here that proposal is `(#1, $20)`, so P2 must send:

```text
Accept(2, $20)    correct
Accept(2, $5)     not allowed by the proposer rule
```

Assuming no higher proposal interrupts the attempt, B and C accept `(#2, $20)`:

| Acceptor | Accepted proposal |
| --- | --- |
| A | `(#1, $20)` |
| B | `(#2, $20)` |
| C | `(#2, $20)` |

The proposal numbers differ, but **all three accepted values are $20** in this example. A new proposal number did not create a new decision or permission to overwrite the chosen value.

**3. Why does this work? Any two majorities overlap**

```text
First majority:   A + B
Second majority:  B + C
Shared acceptor:  B
```

B carries the earlier accepted value into P2's promise quorum. If B had since accepted a higher-numbered proposal, it would report that one instead; the protocol rules ensure it still preserves the chosen value. Quorum overlap works together with **remembered acceptor state** and the **highest-accepted-value selection rule**. [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)

```text
1. PREPARE -> Ask a majority about earlier accepted proposals.
2. PROMISE -> Acceptors promise not to accept lower proposal numbers.
3. SELECT  -> Preserve the highest accepted value, or use a new value if none exists.
4. ACCEPT  -> Request acceptance of that selected value.
5. MAJORITY ACCEPTS -> The value is CHOSEN; learners can learn it from the replies.
```

> **Before writing your value, first ask a majority whether an earlier value must be preserved.** A value being chosen does not mean every replica has already accepted, learned, or applied it; unavailable or delayed nodes can lag behind.

**4. Is $20 permanent? For this slot, yes**

Once $20 is chosen, **that slot's decision cannot change**. A different decision belongs to a **new slot**, not merely a higher proposal number in the same slot:

```text
Slot 1 -> $20
Slot 2 -> $5
Slot 3 -> $30
```

Multi-Paxos / replicated logs build an ordered sequence of such decisions. Each slot has its own consensus instance. The application can change a record through later commands without rewriting earlier chosen log entries.

**5. How does Paxos know $20 is correct? It does not**

Paxos guarantees that **conflicting values cannot both be chosen for the same slot**. It does not decide whether $20 or $5 is valid according to financial rules; that is the application's responsibility.

In a financial application, log entries can instead be commands such as `credit $20` and `credit $5`. If these are two legitimate deposits, they belong to separate decisions so both can be processed, rather than discarding one.

> **Paxos = agreement mechanism; a replicated log adds ordering. Business correctness comes from application logic.**

#### Paxos Challenges

- **Fault tolerance:** The protocol can make progress despite some failures while a majority remains reachable. Losing a majority blocks new decisions.
- **Competing proposers:** Proposers can repeatedly interrupt each other with higher proposal numbers. A stable distinguished proposer or leader helps progress.
- **Scalability:** More participants and distant replicas increase communication and coordination costs. Adding acceptors does not automatically increase write throughput.
- **Complexity:** Retries, reordered messages, crash recovery, and competing proposals must obey the safety rules.
- **Persistent state:** Acceptors must preserve promises and accepted proposals across restarts; forgetting them can break safety.

#### Paxos Variants and Optimizations

| Name | Main idea | Important qualification |
| --- | --- | --- |
| **Multi-Paxos** | Agree on a sequence of values using a stable leader. | The leader can perform prepare for many log positions together and then use accept for subsequent commands. It avoids repeating prepare while that leadership remains valid; it does **not** eliminate the accept phase. |
| **Fast Paxos** | Let clients propose directly to acceptors in an established fast round, reducing a message delay when proposals do not conflict. | Fast rounds generally require larger quorums. Conflicting proposals require recovery, so the fast path is not unconditional. |
| **Paxos Made Simple** | A clearer explanation of the original Paxos algorithm. | It is not a separate one-round protocol called "Simple Paxos" that merges prepare and accept. |

[Multi-Paxos explanation](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), [Fast Paxos](https://www.microsoft.com/en-us/research/publication/fast-paxos/), [Fast Paxos quorum details](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-2005-112.pdf)

#### Paxos Applications

- **Distributed databases:** Agree on ordered updates within a replica group. The published Spanner design uses Paxos replication; transactions across groups need additional coordination.
- **Filesystem metadata and coordination:** Agree on leadership or shared metadata. Google's Chubby uses Paxos, and GFS uses Chubby to appoint its master and store some shared metadata.
- **Replicated state machines:** Agree on commands for key-value stores or other deterministic services; each replica applies the chosen commands in order.

[Spanner design](https://storage.googleapis.com/gweb-research2023-media/pubtools/1974.pdf), [Chubby design and GFS integration](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)

> Paxos is a consensus building block. Correct storage, application rules, and retry handling are still needed to turn agreement into a reliable service.

### Raft

**Raft**, developed by **Diego Ongaro and John Ousterhout** and published in 2014, is a consensus algorithm designed to be easier to understand and implement. It organizes the problem into **leader election**, **log replication**, and **safety**.

Raft maintains an **ordered, replicated log**. Replicas apply committed commands in order to their state machines. Their logs can temporarily differ, but they must not apply conflicting commands at the same log position.

**Hands-on example:** [DSA-style C++17 Raft core](examples/raft/README.md) — short procedures, matching pseudocode, complexity, and a replicated-credit example. [Implementation](examples/raft/raft_dsa.cpp).

#### Raft Roles and Terms

| Role | Responsibility |
| --- | --- |
| **Follower** | Receives log entries and heartbeats, responds to requests, and votes in elections. |
| **Candidate** | Starts an election and asks other servers for votes. |
| **Leader** | Coordinates new log entries, replication, and commitment. |

A **term** is a numbered election period. Servers use term numbers to recognize outdated leaders and messages. Each server grants at most one vote per term; a server discovering a higher term updates its term and becomes a follower.

> A timeout suggests that a leader may be unavailable; it does not prove that the leader has crashed. A delayed network can also trigger an election.

#### Raft State Diagram

```mermaid
stateDiagram-v2
    [*] --> Follower
    Follower --> Candidate: Election timeout / start election
    Candidate --> Candidate: Timeout / start a new election
    Candidate --> Leader: Receive votes from a majority
    Candidate --> Follower: Discover a valid leader or higher term
    Leader --> Follower: Discover a higher term

    classDef role fill:#bdbdbd,stroke:#111,stroke-width:2px,color:#111
    class Follower role
    class Candidate role
    class Leader role
```

**Diagram:** Servers start as followers. A timeout starts an election; a majority of votes makes a candidate the leader. A candidate can retry an unsuccessful election or return to follower when it recognizes a valid leader. A leader steps down when it discovers a higher term.

#### Raft Protocol Steps

1. **Leader election:** A follower whose election timer expires becomes a candidate, increments its term, votes for itself, and sends `RequestVote` messages. A majority of votes elects the leader. Randomized timeouts reduce repeated split votes.
2. **Receive a command:** The leader receives a client request and appends a log entry containing the command, its term, and its position in the log.
3. **Replicate the log:** The leader sends `AppendEntries` messages to followers. Followers check the preceding log entry and store matching updates; the leader retries or repairs inconsistent log suffixes. Heartbeats are `AppendEntries` messages without new entries.
4. **Commit:** An entry from the leader's current term can be committed once stored on a majority, including the leader. Committing it also commits preceding entries. An older-term entry is not committed merely by counting copies; commitment must follow Raft's current-term rule.
5. **Apply and respond:** The leader applies committed commands in order and returns the result. Followers learn the commit position and apply committed entries in the same order. Receiving an entry alone does **not** make it safe to apply.

**Hotel-room example:** The leader records `BookRoom(u1, r1)` and replicates it. After commitment, replicas apply the command's atomic availability check and booking update. A later command for the same room sees it as booked. The application still needs request IDs or deduplication so client retries do not create duplicate operations.

#### Raft Safety Rules

| Rule | What it prevents |
| --- | --- |
| **Election safety** | Two leaders being elected in the same term. |
| **Voting restriction** | Electing a candidate whose log is not sufficiently up to date. Log freshness is compared by the last entry's term, then its index. |
| **Log matching** | Two logs with the same entry index and term having different preceding histories. `AppendEntries` checks and repairs the matching prefix. |
| **Leader completeness** | A future leader omitting an entry that was already committed. |
| **State-machine safety** | Different replicas applying different commands at the same log position. |

Servers persist the current term, their vote, and log entries before the relevant acknowledgements. Together with the election and commit rules, this lets safety survive crashes and restarts. [Raft paper](https://raft.github.io/raft.pdf)

#### Raft Challenges

- **Leader availability:** New writes need a functioning leader and a communicating majority. An election temporarily delays progress.
- **Scalability:** The leader coordinates replication and can become a bottleneck. Additional voting replicas add communication and storage work; large datasets may need multiple consensus groups.
- **Network delays:** Poorly chosen timeouts or unstable networks can trigger unnecessary elections.
- **Fault tolerance:** A majority can keep making progress while some servers fail. A minority partition cannot safely commit new entries on its own.
- **Implementation:** Durable state, log repair, snapshots, membership changes, and client retries still need careful handling, despite Raft's clearer structure.
- **Failure model:** Standard Raft handles crashes, not malicious nodes that invent votes or send dishonest log entries.

#### Raft Applications

- **Distributed databases and key-value stores:** Replicate commands and maintain an agreed history; etcd is a documented Raft-based example.
- **Filesystem metadata services:** A Raft-based metadata service can agree on namespace updates or leadership; the specific filesystem's implementation must be checked.
- **Cluster coordination and service discovery:** Agree on configuration, membership, service registrations, or locks. Consul uses Raft for its server state.
- **Replicated state machines and consensus-based services:** Apply an agreed sequence of commands to maintain consistent application state.
- **Cloud infrastructure management:** Coordinate resource allocations or control-plane decisions; this is a possible use of Raft, not proof that every infrastructure platform uses it.

[etcd Raft implementation](https://go.etcd.io/etcd/raft/v3), [Consul's consensus design](https://developer.hashicorp.com/consul/docs/concept/consensus)

#### Named Systems and Algorithm Boundaries

Consensus is useful in all these areas, but the product's actual algorithm matters:

| System | Relevant use | Algorithm or qualification |
| --- | --- | --- |
| **Amazon DynamoDB** | Distributed database with eventual and strongly consistent read options. | These API options do not establish that its internal protocol is Raft. Treat it as a database example rather than an unverified Raft deployment. [AWS documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html) |
| **Google File System (GFS)** | Distributed storage, metadata, and master coordination. | The original GFS predates Raft. The Chubby paper describes Paxos-based coordination used to appoint the GFS master, rather than Raft replication of GFS metadata. [Chubby paper](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf) |
| **Hadoop HDFS** | Replicated storage and NameNode high availability. | Documented automatic failover uses ZooKeeper coordination; this does not make HDFS a direct Paxos or Raft implementation. [HDFS HA documentation](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html) |
| **Apache ZooKeeper** | Shared metadata, leader election, configuration, and coordination. | Uses **Zab**, its atomic-broadcast protocol, rather than Raft. [ZooKeeper documentation](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html) |
| **Google Spanner** | Consistent replication and distributed transactions. | The published design uses **Paxos** within replication groups. [Spanner paper](https://storage.googleapis.com/gweb-research2023-media/pubtools/1974.pdf) |
| **Netflix ChAP** | Automated chaos experiments that test service resilience. | Its documented purpose is failure testing; it is not a verified example of Raft-based resource management. [Netflix's ChAP description](https://netflixtechblog.com/chap-chaos-automation-platform-53e6d528371f) |
| **etcd and Consul** | Consistent metadata storage and cluster coordination. | Both have documented **Raft** implementations. [etcd](https://go.etcd.io/etcd/raft/v3), [Consul](https://developer.hashicorp.com/consul/docs/concept/consensus) |

### Zab and ZooKeeper

**ZooKeeper** is a coordination service. **Zab (ZooKeeper Atomic Broadcast)** is the protocol it uses to replicate an **ordered stream of updates**.

> **ZooKeeper = the service; Zab = its replication protocol.** *Atomic broadcast* means correct replicas deliver the same committed updates in the same order, not necessarily at the same instant.

The simplified workflow is:

1. **Establish leadership:** Select a leader and synchronize its history with a quorum before accepting new updates.
2. **Propose:** The leader gives each update a transaction ID, **`zxid`**, containing a leadership epoch and a counter, and sends updates in order.
3. **Acknowledge and commit:** Voting replicas record proposals and acknowledge them. With a quorum, the leader announces commitment; replicas apply committed updates in order.
4. **Recover:** After a leader failure, synchronize the replacement leader and followers while preserving committed history.

**Example:** Three ZooKeeper servers store a shared configuration. The leader proposes `timeout = 30`; two voting servers record it, forming a majority. The update commits. If the leader later fails, recovery preserves that committed update.

> **Ordered writes do not guarantee fresh local reads.** An ordinary ZooKeeper read can return an older value from a lagging replica. Zab is crash-tolerant, not Byzantine-tolerant. [ZooKeeper replication and consistency guarantees](https://zookeeper.apache.org/doc/current/zookeeperInternals.html)

### Other Protocols to Study Later

**Core study set:** Paxos/Multi-Paxos, Raft, Zab, and **PBFT**. PBFT addresses Byzantine faults and is covered in [Classical Solutions and PBFT](#classical-solutions-and-pbft), rather than treated as a crash-tolerant alternative.

Other useful names to recognize, without studying every detail yet:

- **Viewstamped Replication (VR):** Leader-based replicated services with recovery and leadership changes after crashes. [VR paper](https://dspace.mit.edu/entities/publication/80846d94-fcd3-40e6-87fb-8d91fe99a5d1)
- **EPaxos (Egalitarian Paxos):** A Paxos-based protocol that distributes proposal coordination across replicas rather than relying on one fixed leader. [EPaxos paper](https://www.pdl.cmu.edu/PDL-FTP/associated/epaxos-sosp2013_abs.shtml)
- **HotStuff:** A leader-based Byzantine-tolerant replication protocol that improves communication efficiency under its stated assumptions. [HotStuff paper](https://arxiv.org/abs/1803.05069)

### Paxos vs. Raft vs. Zab

| Aspect | Paxos | Raft | Zab |
| --- | --- | --- | --- |
| Basic unit | One chosen value; Multi-Paxos builds an ordered log. | An ordered, replicated log. | An ordered stream of replicated updates. |
| Roles | Proposer, acceptor, learner; roles may share a server. | Follower, candidate, leader; a server changes state. | Leader and followers; ZooKeeper can also use non-voting observers. |
| Leadership | Basic Paxos can have competing proposers; Multi-Paxos usually uses a stable leader. | Leader election and leader-driven log replication are explicit parts of the protocol. | Leadership activation synchronizes histories before normal broadcasting. |
| Main emphasis | Safe agreement through proposal numbers, promises, and intersecting quorums. | Understandable consensus through election, log replication, and safety rules. | Ordered delivery and preservation of committed history across leadership changes. |
| Standard fault model | Crashes and communication failures, not Byzantine behavior. | Crashes and communication failures, not Byzantine behavior. | Crashes and communication failures, not Byzantine behavior. |

[Paxos](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), [Raft](https://raft.github.io/raft.pdf), [Zab](https://zookeeper.apache.org/doc/current/zookeeperInternals.html)

> All three can support reliable replicated services. None guarantees progress without the required quorum, and none removes the need for correct application logic. Byzantine failures require a different fault model and suitable protocols; see the [Byzantine Generals Problem](#byzantine-generals-problem-bgp).

## Byzantine Generals Problem (BGP)

The **Byzantine Generals Problem** asks: **How can correct nodes agree when some participants can lie, send conflicting messages, or stop responding?**

> **Remember:** A failed node may do more than go silent; it may give different answers to different nodes. Agreement must remain safe despite those answers.

Here, **BGP** means *Byzantine Generals Problem*, not the networking protocol *Border Gateway Protocol*.

### The Generals Example

Generals surround a city and communicate through messengers. They must agree to **attack** or **retreat**, but some may be traitors. Loyal generals cannot reliably identify traitors, and traitors may cooperate to confuse them.

**Example:** A traitorous commander tells one loyal general to attack and another to retreat:

```mermaid
flowchart TB
    T["Traitorous commander"]
    A["Loyal general A<br/>Received: Attack"]
    B["Loyal general B<br/>Received: Retreat"]
    T -->|Attack| A
    T -->|Retreat| B
    A <-->|Compare received orders| B

    classDef loyal fill:#d7efdf,stroke:#111,stroke-width:2px,color:#111
    classDef faulty fill:#f8d7da,stroke:#111,stroke-width:2px,color:#111
    class A,B loyal
    class T faulty
```

**Diagram:** A and B received contradictory orders. Without verifiable evidence, each cannot tell whether the commander or the other general is lying. Simply exchanging messages once does not solve the problem. [Original Byzantine Generals paper](https://lamport.azurewebsites.net/pubs/byz.pdf)

### Requirements for Byzantine Agreement

| Requirement | Simple meaning | Generals example |
| --- | --- | --- |
| **Agreement — safety** | Correct participants must not decide conflicting values. | Loyal generals must not split into attack and retreat decisions. |
| **Validity** | The decision must satisfy the protocol's validity rule. In the commander version, a correct commander's order must be followed. | A loyal commander's attack order cannot be replaced by retreat. |
| **Termination — liveness** | Correct participants eventually decide under the protocol's fault and communication assumptions. | Loyal generals eventually settle on a plan rather than wait forever. |

> **These guarantees must hold despite up to $f$ faulty participants, within the protocol's stated assumptions.** In the classical oral-message model and Practical Byzantine Fault Tolerance (PBFT), tolerating $f$ Byzantine faults requires at least $3f + 1$ participants. Correct nodes must eventually decide when communication satisfies the protocol's progress assumptions; deciding quickly is an additional performance goal.

> Agreement does not automatically make a decision financially or operationally correct. Applications still validate commands and enforce business rules.

### Byzantine Faults vs. Crash Faults

A **Byzantine fault** is arbitrary incorrect behavior. It may result from a software bug, hardware corruption, or a malicious attack; intentional dishonesty is not required. Faulty nodes may also collude. [PBFT fault model](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node2.html)

| Fault | Behavior | Example |
| --- | --- | --- |
| **Crash fault** | A node stops executing or responding. | A database server shuts down. |
| **Byzantine fault** | A node can invent, alter, contradict, or withhold information. | A replica reports a payment as approved to A but rejected to B. |

**Sending conflicting messages about the same decision is called _equivocation_.** An ordinary network delay alone does not prove Byzantine behavior: an honest node may simply be unreachable.

> Standard **Paxos and Raft handle crash faults, not arbitrary dishonest participants**. Adding replicas to either algorithm does not, by itself, make it Byzantine fault tolerant.

### Byzantine Fault Tolerance and Quorums

**Byzantine fault tolerance (BFT)** means preserving the specified correct behavior despite up to a defined number of Byzantine participants. It is a property; **PBFT** is one protocol that provides it under stated assumptions.

For the classical *oral-message* model and PBFT-style replication, the familiar bound is:

$$
N \geq 3f + 1
$$

where **$N$** is the number of participants and **$f$** is the maximum number that may be Byzantine (faulty or malicious nodes). A simple honest majority is not enough in these models. [Classical fault bound](https://lamport.azurewebsites.net/pubs/byz.pdf), [PBFT replica bound](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

**The “one-third rule”:** In the classical oral-message model and PBFT, Byzantine participants must constitute **strictly less than one-third** of the group:

$$
f < \frac{N}{3}
$$

For **4 nodes**:

- **1 faulty node:** $1/4 = 25\%$ — within the tolerated limit.
- **2 faulty nodes:** $2/4 = 50\%$ — beyond the limit; correct agreement is **no longer guaranteed**. [PBFT fault bound](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

> **Remember: less than one-third—not “up to 33%.”** Exceeding the limit means losing the guarantee, not that agreement becomes impossible in every execution.

For a group sized **$N = 3f + 1$**, a typical agreement quorum contains **$2f + 1$ distinct replicas**:

| Byzantine faults tolerated ($f$) | Group size ($3f + 1$) | Quorum size ($2f + 1$) |
| ---: | ---: | ---: |
| 1 | 4 | 3 |
| 2 | 7 | 5 |
| 3 | 10 | 7 |

**Why this helps — four-node example:** With A, B, C, and D, any two three-node quorums share at least two nodes. If at most one node is Byzantine, at least one shared node is correct. The protocol uses that honest overlap and remembered votes to prevent conflicting decisions.

The overlap follows directly from:

$$
|Q_1 \cap Q_2| \geq 2(2f + 1) - (3f + 1) = f + 1
$$

**Progress:** If D refuses to respond, A, B, and C can still form a quorum. If only two nodes are reachable, they cannot form this quorum; new decisions must wait rather than become unsafe.

> **These numbers depend on the fault model and protocol.** They are not universal rules for every BFT system. For larger groups, quorum sizes must be recalculated to preserve honest overlap; do not blindly keep $2f + 1$.

PBFT preserves safety despite arbitrary delays within its fault bound. Progress requires communication to become timely enough for its timeout and leader-change mechanisms to succeed; it does not promise a fixed completion time during an indefinite partition. [PBFT safety and liveness assumptions](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

### Common BFT Techniques

These are **building blocks used together**, not five interchangeable, complete consensus algorithms:

| Technique | How it helps | Important limitation |
| --- | --- | --- |
| **Multi-round voting** | Nodes exchange proposals and evidence before deciding. | One local majority vote is insufficient; different nodes may receive different messages. A vote threshold alone (for example, a 2/3 majority) is not a complete solution. Nodes need rules for handling conflicting votes, multiple rounds, and earlier decisions. |
| **Authentication and signatures** | Verify who sent a message and whether it was altered; signed contradictions can provide evidence of misbehavior. | A signature proves the sender, not the truth. Failure to sign does not prove that a node is a traitor. **Not signing does not prove someone is a traitor.** An honest node might miss the request or be disconnected. A signature proves who signed—not whether they are honest. |
| **Intersecting quorums** | Decision groups share enough correct participants to carry earlier evidence forward. | Honest majorities inside separate groups are not enough; their intersections and voting rules must also be safe. Nodes are not simply divided into independent groups. Decision quorums must **overlap in enough honest nodes**, and those nodes must follow rules that prevent conflicting decisions. |
| **Timeouts and leader changes** | Suspect a stalled leader and attempt progress with another. | Silence may mean delay or disconnection, not malice. Removing members requires a safe reconfiguration protocol. A timeout justifies **suspicion**, not proof of dishonesty. Conflicting signed messages can provide evidence, but removing participants requires safe membership-change rules. |
| **Randomization** | Random choices or a shared random coin help some protocols escape repeated disagreement. | A random nonce does not identify honest nodes. Randomized protocols still require precise fault and delivery assumptions. **Knowing a random nonce does not prove loyalty.** Randomized agreement uses random choices to help nodes eventually agree, not to identify honest participants. |

[Signed-message reasoning](https://lamport.azurewebsites.net/pubs/byz.pdf), [PBFT voting and view changes](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node4.html), [Randomized Byzantine agreement](https://eprint.iacr.org/2000/034)

### Classical Solutions and PBFT

**Lamport, Shostak, and Pease** described two classical approaches:

- **Oral messages:** Relay received orders through multiple rounds and combine them using a defined decision rule. Assume known senders, correct delivery between loyal nodes, and detectable missing messages. This is not merely one all-to-all majority vote.
- **Signed messages:** Forward verifiable signed orders. The classical synchronous signed-message solution can tolerate more traitors than the oral-message bound; this does not remove PBFT's separate replica requirement.

[Original algorithms and assumptions](https://lamport.azurewebsites.net/pubs/byz.pdf)

**Hands-on example:** [DSA-style C++17 classical oral-message agreement](examples/bft/README.md) — recursive OM(m), matching pseudocode, complexity, conflicting messages, and an outside-fault-bound counterexample. [Implementation](examples/bft/bft_dsa.cpp). This is the classical generals algorithm, not PBFT.

**Practical Byzantine Fault Tolerance (PBFT)**, introduced by **Miguel Castro and Barbara Liskov**, makes Byzantine-tolerant replicated services practical through authenticated messages, voting phases, and leader changes. [PBFT paper](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/castro.html)

Its normal request path is:

1. **Pre-prepare:** The primary proposes a request and its log position.
2. **Prepare:** Replicas exchange matching evidence about that proposal.
3. **Commit:** A prepared replica collects $2f + 1$ matching commit messages, including its own if applicable, before executing the request in log order.
4. **Reply:** The client accepts the result after receiving $f + 1$ matching authenticated replies from distinct replicas. If the primary stalls, replicas use a **view change** to select another while preserving prior evidence.

> **Different thresholds serve different purposes:** $2f + 1$ commit messages establish replication evidence; $f + 1$ matching client replies include at least one correct replica. PBFT does not use the same threshold at every step.

[PBFT protocol steps](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node4.html)

### When Is BFT Needed?

**Choose fault tolerance based on the failures the system must withstand—not merely whether the network is “trusted.”**

| Assumed failures | Suitable approach |
| --- | --- |
| Nodes crash, disconnect, or experience delayed messages, but otherwise follow the protocol | **Crash-fault tolerance**, such as Paxos or Raft |
| Some participants may lie, send contradictory messages, or behave arbitrarily, while correct participants must still agree | **Byzantine fault tolerance**, using a suitable protocol |

**CFT is often sufficient** for internally managed replicated services when arbitrary participant behavior is outside the accepted fault model.

**BFT is useful when agreement must survive participants behaving dishonestly or incorrectly. Examples include:**

- **Compromised nodes:** A hacked server tells one replica “payment approved” and another “payment rejected.” BFT can preserve consistent agreement despite a limited number of such faulty participants. [PBFT fault model](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node2.html)

- **Blockchains:** Participants must agree on transactions even when some validators cheat. Ethereum uses proof-of-stake consensus with Casper-FFG finality. Hyperledger Fabric supports both **crash-tolerant Raft** and **Byzantine-tolerant ordering**, depending on the deployment. [Ethereum consensus](https://ethereum.org/developers/docs/consensus-mechanisms/pos/), [Fabric ordering services](https://hyperledger-fabric.readthedocs.io/en/latest/orderer/ordering_service.html)

- **Shared systems between organizations:** Several banks maintain a shared settlement ledger. If the design must withstand one bank’s server sending conflicting transaction records, BFT can help the correct participants maintain a consistent ledger. **This does not prove that every submitted transaction is legitimate**; authorization and business validation remain necessary. [PBFT guarantees and limitations](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

> **The deciding factor is the required failure protection—not simply “blockchain,” “financial,” or “high-stakes.”** Use CFT when participants are assumed to follow the protocol; consider BFT when agreement must remain correct even when some participants violate it.

> **Trusted does not mean incapable of Byzantine failure.** Software bugs, corruption, or compromised machines can cause arbitrary behavior even within one organization. [PBFT fault model](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node2.html)

Avoid saying that **all decentralized, financial, aviation, or high-stakes systems require BFT**. Their requirements and architectures differ. Likewise, BFT preserves specified protocol guarantees; it does not automatically prevent fraud, validate external facts, or guarantee physical safety. [PBFT guarantees and limitations](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

**Recall:** CFT assumes participants follow the protocol until they fail; BFT allows some participants to violate it.

### BFT Applications and Trade-Offs

- **Replicated services:** Protect agreement and command order when some replicas may be compromised or incorrect. PBFT's original implementation demonstrated a replicated filesystem service.
- **Blockchains:** Participants must agree despite adversarial behavior, but their algorithms differ. **Bitcoin uses proof of work**, not PBFT; **Ethereum uses proof of stake with Casper-FFG finality**, where voting weight depends on stake rather than a simple node count. [Bitcoin design](https://bitcoin.org/bitcoin.pdf), [Ethereum consensus and finality](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/)
- **Costs:** Extra replicas, authentication, evidence storage, and multiple communication rounds increase cost and complexity. PBFT's normal all-to-all voting has **$O(N^2)$ message exchanges**; it is not automatically suitable for an arbitrarily large network. This follows from its prepare and commit broadcasts. [PBFT message pattern](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node4.html)
- **Failure independence:** Replicas sharing one exploitable bug or compromised administrator may fail together and exceed the assumed fault budget. Diversity and operational isolation matter. [PBFT system assumptions](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node2.html)

> **BFT = agreement despite some dishonest or arbitrarily faulty participants, within a defined fault budget.** It does not require identifying every faulty node, guarantee uninterrupted progress under all network conditions, or replace application validation and security controls.

### BFT and AI/LLM-Based Systems

**BFT handles more than silent failures.** A faulty participant may lie, send contradictory messages, corrupt its state, or stop responding. The behavior need not be intentional. BFT protocols protect the specified agreement process within their fault and network assumptions. [PBFT fault model](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node2.html)

However, **an LLM giving different answers is not automatically a Byzantine fault**. Different answers can be normal model behavior. The important question is whether a participant violates the rules the system requires it to follow.

| Problem | Appropriate approach |
| --- | --- |
| A replica crashes or becomes unreachable | Crash-tolerant replication, such as Paxos or Raft |
| A replica lies, equivocates, or violates the protocol | A suitable BFT protocol, such as PBFT |
| An LLM invents an unsupported claim | Grounding, evidence checks, evaluation, and appropriate human review |
| AI agents reach different conclusions | Evidence-based verification and an explicit decision or escalation policy—not merely majority voting |

**Example: Four robots assess a bridge.**

- A, B, and C report **“safe.”**
- D reports **“unsafe.”**

BFT could protect the agreement process against a faulty participant—for example, one sending conflicting coordination messages. But **three “safe” reports do not prove that the bridge is safe**. They might share the same mistaken assumption or unreliable evidence. Disagreement alone also does not prove that D is faulty.

> **BFT protects agreement despite faulty participants. AI validation checks whether the agreed information or proposed action is actually justified.**

PBFT can tolerate one Byzantine replica among four under its assumptions; simply taking three matching AI answers is not PBFT. Its original replicated-service design assumes deterministic operations, so independently generated LLM answers are not interchangeable with deterministic replica execution. [PBFT service properties](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/node3.html)

For the AI-side controls, see [Distributed Agreement vs. AI Answer Correctness](AI-Systems-Design.md#distributed-agreement-vs-ai-answer-correctness).

## FLP Impossibility Theorem

The **FLP impossibility theorem**, named after **Michael J. Fischer, Nancy A. Lynch, and Michael S. Paterson**, was published in its journal form in **1985**.

**No deterministic consensus algorithm can guarantee that a valid, consistent decision will eventually be reached in every execution of a fully asynchronous message-passing system when even one process may crash.** [Original FLP paper](https://cs.nyu.edu/~apanda/classes/sp25/papers/fischer85impossibility.pdf)

> **Remember:** Nodes can preserve agreement, yet be unable to guarantee that they will ever finish deciding. FLP limits the guarantee of progress—not the possibility of reaching consensus in ordinary runs.

### Consensus Requirements

Consensus turns participants' proposals into one shared decision. For example, replicas may need to agree on which transaction occupies the next log position.

| Requirement | Simple meaning | Example |
| --- | --- | --- |
| **Agreement** | Correct processes do not decide different values for the same decision. | Replicas do not commit different transactions into the same log position. |
| **Validity** | The decision satisfies the consensus problem's input rules, rather than being an unrelated fixed answer. | In a common formulation, the selected value must have been proposed; if everyone proposes the same value, it must be selected. |
| **Termination** | Every correct process eventually decides. | Replicas do not remain undecided forever. |

Agreement and validity are **safety** requirements: do not make an invalid or conflicting decision. Termination is **liveness**: eventually finish. Validity here does not mean a transaction is financially legitimate; application validation is separate.

### FLP Assumptions

| Assumption | What it means |
| --- | --- |
| **Fully asynchronous communication and processing** | There is no known upper bound on message delay or the time between a process's steps. Silence cannot establish that a process crashed. |
| **Deterministic algorithm** | The same local state and received input produce the same next action; no random choices are used. |
| **Possible crash failure** | Even one process may permanently stop. It need not lie or behave maliciously. |
| **Reliable eventual delivery and fair execution** | Messages to correct processes eventually arrive, and correct processes keep taking steps—but neither has a bounded waiting time. |

The impossibility does **not** require lost messages, Byzantine behavior, or a permanent network partition. The theorem's model has discrete local steps; it does not assume that an entire execution contains only finitely many steps. A nonterminating run can continue indefinitely. [FLP model and result](https://cs.nyu.edu/~apanda/classes/sp25/papers/fischer85impossibility.pdf)

### FLP Impossibility Triangle

The textbook-style triangle is a **memory aid**, conditional on deterministic, fully asynchronous operation and a nontrivial validity requirement:

```mermaid
block-beta
    columns 3

    H["<b>FLP Impossibility Triangle</b><br/>Deterministic + fully asynchronous"]:3

    space
    F["<b>Fault tolerance</b><br/>Even one possible crash"]
    space

    space:3

    T["<b>Termination</b><br/>Every correct process<br/>eventually decides"]
    space
    A["<b>Agreement</b><br/>No conflicting decisions"]

    F --- T
    F --- A
    T --- A

    classDef property fill:#fff,stroke:#111,stroke-width:2px,color:#111
    class F,T,A property
    style H fill:transparent,stroke:transparent,color:#111
```

**Diagram:** Under those assumptions, valid agreement, guaranteed termination, and tolerance of even one possible crash cannot all be provided by a deterministic protocol.

> **This is not a universal “choose any two” design menu.** Fault tolerance is a requirement about the failures to withstand. Practical protocols usually preserve safety and guarantee progress only under additional conditions.

### Why a Slow Node Looks Like a Failed Node

Imagine three database replicas, **A, B, and C**, trying to agree on the next transaction. C's expected message has not arrived:

- **Possibility 1:** C crashed and will never reply.
- **Possibility 2:** C is healthy, but its message is taking much longer than expected.

Without a delivery-time bound or additional failure information, A and B cannot tell which happened. **Waiting indefinitely** can block completion after a crash. **Deciding without sufficient protocol evidence** can risk conflicting decisions. A timeout signals suspicion, not proof of a crash.

Quorum protocols can often proceed without C, but a majority alone does not remove FLP: carefully timed delays can repeatedly disrupt progress while the protocol keeps agreement safe.

**Proof intuition:** Some starting states still permit either decision. The proof constructs a fair message/step schedule that keeps the system undecided indefinitely; correct processes continue working and their messages eventually arrive. This is a worst-case possibility, not a prediction that typical deployments will always stall. [FLP proof](https://cs.nyu.edu/~apanda/classes/sp25/papers/fischer85impossibility.pdf)

### What FLP Does and Does Not Say

- **It says:** A deterministic protocol cannot guarantee valid agreement and termination in every allowed fully asynchronous execution when a process may crash.
- **It does not say:** Every run fails, a crash must actually occur, or Paxos and Raft are incorrect.
- **It does not say:** Adding more replicas or choosing a leader automatically restores guaranteed progress.
- **It does not say:** Consensus must finish within a deadline. Even eventual termination cannot be guaranteed under the original assumptions.

For **Paxos and Raft**, distinguish **safe decisions** from **progress**. A usable quorum and sufficiently stable communication and leadership support completion; arbitrary continued delays or competing leadership attempts can prevent it. [Paxos safety and progress](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), [Raft elections and timing](https://raft.github.io/raft.pdf)

### How Practical Systems Make Progress

Systems do not disprove FLP; they change the assumptions or the termination guarantee:

| Approach | What changes | Important qualification |
| --- | --- | --- |
| **Synchronous timing assumptions** | Known bounds on communication and processing make time-based reasoning possible. | The protocol's progress guarantee depends on those bounds holding and its fault limit not being exceeded. |
| **Partial synchrony** | Communication and processing eventually become timely enough, even if the stabilization time is unknown. | This supports progress after stabilization, not a guaranteed deadline throughout arbitrary disruption. |
| **Randomized consensus** | The protocol uses random choices instead of being fully deterministic. | Suitable protocols can terminate with probability 1 under their stated fault and scheduling assumptions; this is not a fixed-time guarantee. |
| **Failure detectors with specified guarantees** | Additional information eventually supplies enough useful failure or leadership information. | A detector may initially make mistakes. Its required accuracy/completeness guarantees—not merely having heartbeats—enable progress. |

[Partial synchrony](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf), [Randomized consensus](https://arxiv.org/html/cs/0209014), [Failure detectors](https://www.cs.cornell.edu/courses/cs734/2000FA/cached%20papers/ct96.pdf)

**A leader alone is not an escape:** it may crash or remain unreachable. **Clock synchronization alone is not an escape:** matching timestamps does not impose a bound on message delivery or provide the missing failure information. Timeouts and leader election are useful mechanisms when combined with the required progress assumptions.

**Connection to the BFT example:** The [classical OM(m) simulation](examples/bft/README.md) assumes synchronous rounds and detectable missing messages. It therefore does not operate under FLP's fully asynchronous assumptions; its successful agreement is not a contradiction.

### Kafka Example: FLP and KRaft

**FLP applies to Kafka's KRaft controller quorum**, which uses Raft-based consensus to agree on **cluster metadata**. This example concerns metadata coordination, not a claim that every Kafka topic's data is replicated using Raft.

Imagine **three controllers: A, B, and C**. A majority is **two**:

- **C crashes:** A and B can normally continue making metadata decisions if they can communicate and establish stable leadership.
- **The leader becomes unreachable:** The remaining two can elect a replacement when communication is timely enough.
- **Communication remains arbitrarily delayed:** Elections or new metadata decisions may keep retrying without completing. Having two running controllers is not enough if they cannot exchange the necessary messages.

**Timeouts trigger election attempts; they do not prove that a controller has crashed.** Kafka therefore does not contradict FLP: it preserves consensus safety, while progress requires a communicating quorum and suitable timing conditions. [Kafka KRaft documentation](https://kafka.apache.org/43/operations/kraft/)

> **Recall:** Kafka can tolerate a controller failure, but it cannot guarantee that metadata consensus finishes under every possible pattern of network delays.

### FLP vs. CAP

| Result | Main limitation |
| --- | --- |
| **FLP** | Deterministic consensus cannot guarantee termination in every fully asynchronous execution with even one possible crash while preserving valid agreement. |
| **CAP** | During a network partition, a distributed read/write service cannot guarantee both linearizable consistency and availability. |

> **Recall:** FLP explains why guaranteed completion needs more than pure asynchrony. CAP explains why partitions force a consistency/availability choice. They are related limits, but not the same theorem.

## Consistent Hashing

**Consistent hashing** assigns keys to servers so that adding or removing a server changes **only part of the assignment**, rather than redistributing most keys. It is useful when a distributed cache, storage cluster, or request-routing layer grows or loses nodes. [Original consistent hashing paper](https://people.csail.mit.edu/karger/Papers/web.pdf)

> **Mental model:** Put servers and keys on a ring. A key belongs to the first server clockwise. Changing a server changes nearby ownership—not the entire ring.

Here, *consistent* means **stable key placement when membership changes**. It does **not** mean strong consistency between database replicas.

### Why Modulo Hashing Causes Reorganization

A simple way to select one of $N$ servers is:

$$
\text{server index} = h(\text{key}) \bmod N
$$

**Example:** Suppose a key's hash is `14`:

- With **4 servers**, `14 % 4 = 2`: send it to server2.
- With **5 servers**, `14 % 5 = 4`: send it to server4.

Changing $N$ changes the destination of many keys. Stored data may need migration; cached data may need to be fetched again, increasing backend load.

| Approach | How a server is selected | When membership changes |
| --- | --- | --- |
| **Modulo hashing** | Compute `h(key) % N` | Many keys map to different servers because the divisor changes. |
| **Consistent hashing** | Find the key's clockwise successor on a hash ring | Only keys whose successor changes need a new owner. |

> The **hash function itself does not need to change** in modulo hashing. The changed divisor is what changes the mapping.

### How the Hash Ring Works

1. **Choose a fixed hash space:** For example, positions `0–99` for illustration. Real systems use a much larger range.
2. **Hash server identifiers:** Each server gets a position called a **token**.
3. **Hash a key:** A cache key, partition key, or routing key gets a position in the same space.
4. **Find its owner:** Select the first token at or after the key's position, moving **clockwise**.
5. **Wrap around:** If the key is beyond the last token, continue from the smallest token.

A token owns the interval **after the previous token, up to and including itself**:

$$
\text{owned range} = (\text{previous token},\ \text{current token}]
$$

The interval wraps across the end of the hash space when necessary. For unchanged membership, everyone using the same hash function and token map computes the same owner.

**Request-routing example:** Hashing a stable key such as `customer_id` sends that customer's requests to the same server. Hashing unrelated request IDs also assigns requests, but does not preserve customer or session affinity.

### Simple Ring Example

Assume these illustrative hash results:

| Server | Token | Owned positions |
| --- | ---: | --- |
| server0 | `s0 = 10` | `(85, 10]`, wrapping through `99 → 0` |
| server1 | `s1 = 35` | `(10, 35]` |
| server2 | `s2 = 60` | `(35, 60]` |
| server3 | `s3 = 85` | `(60, 85]` |

```mermaid
block-beta
    columns 3
    space S0(("s0 = 10<br/>server0")) space
    S3(("s3 = 85<br/>server3")) R["Hash ring<br/>0–99<br/>Clockwise ownership"] S1(("s1 = 35<br/>server1"))
    space S2(("s2 = 60<br/>server2")) space

    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S0

    classDef server0 fill:#b00000,stroke:#fff,color:#fff
    classDef server1 fill:#b86600,stroke:#fff,color:#fff
    classDef server2 fill:#55aa00,stroke:#fff,color:#fff
    classDef server3 fill:#073db5,stroke:#fff,color:#fff
    class S0 server0
    class S1 server1
    class S2 server2
    class S3 server3
    style R fill:transparent,stroke:transparent,color:#111
```

**Diagram:** Arrows show clockwise order in hash space, **not network connections between servers**. Keys are assigned as follows:

| Key/request | Hash position | First token clockwise | Owner |
| --- | ---: | --- | --- |
| `r1` | `20` | `s1 = 35` | server1 |
| `r2` | `40` | `s2 = 60` | server2 |
| `r3` | `70` | `s3 = 85` | server3 |
| `r4` | `95` | `s0 = 10`, after wrapping | server0 |

For example, `r1` lands between `s0` and `s1`. Moving clockwise reaches `s1` first, so **server1 handles `r1`**.

### Adding or Removing a Server

Consider each change **independently, starting from the original ring above**:

| Change | Affected range | Example | What stays unchanged? |
| --- | --- | --- | --- |
| **Add server4 at position 50** | `(35, 50]` changes from server2 to server4. | `r2 = 40` moves to server4; a key at `55` stays on server2. | `r1`, `r3`, and `r4` keep their owners. |
| **Remove server1 at position 35** | `(10, 35]` changes from server1 to server2, its next surviving clockwise neighbor. | `r1 = 20` moves to server2. | `r2`, `r3`, and `r4` keep their owners. |

**Why this helps:** Other servers keep their existing tokens. Only the affected ranges need reassignment. In a storage system, a separate migration process must actually transfer the data.

> **Reassignment is not recovery.** If a failed server held the only copy, choosing a new owner cannot recreate the lost data. Replicas or backups are still needed.

### Problems with One Token per Server

- **Uneven ranges:** Hashes do not necessarily place servers equally far apart. A server owning a large interval may receive more keys than others.
- **Concentrated failover load:** If one server is removed, its entire range goes to one successor. That server may overload and fail too, potentially causing a **cascading failure**.

**Example:** If server1 was serving 1,000 requests/second and is removed, server2 may inherit those requests on top of its own traffic. Without spare capacity, server2 can become overloaded.

Even equal-sized ranges do not guarantee equal workload: one popular key may receive far more requests than thousands of other keys.

### Virtual Nodes: Multiple Tokens per Server

**Virtual nodes (vnodes)** give each physical server **several positions on the ring**. Each token owns a small range, but requests still go to its corresponding physical server.

Instead of one position plus three extra *dummy points*, think of **four tokens representing the same machine**:

| Physical server | Its four ring tokens | Actual servers represented |
| --- | --- | ---: |
| server0 | `s0`, `s01`, `s02`, `s03` | 1 |
| server1 | `s1`, `s11`, `s12`, `s13` | 1 |
| server2 | `s2`, `s21`, `s22`, `s23` | 1 |
| server3 | `s3`, `s31`, `s32`, `s33` | 1 |

You can generate these positions with **one hash function** and different token identifiers:

```text
token(server0, 0) = h("server0#0") → s0
token(server0, 1) = h("server0#1") → s01
token(server0, 2) = h("server0#2") → s02
token(server0, 3) = h("server0#3") → s03
```

Separate hash functions `h`, `h1`, `h2`, and `h3` are **an option, not a requirement**. The important point is to obtain multiple well-distributed, distinct token positions.

**Benefits:** Multiple tokens can improve balance and spread a joining or departing server's ranges across several neighbors. Cassandra uses multiple tokens per physical node for this purpose. [Cassandra's token-ring and vnode explanation](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html#multiple-tokens-per-physical-node-vnodes)

### Enhanced Ring Diagram

```mermaid
block-beta
    columns 7
    space:2 S0(("s0")) S1(("s1")) S2(("s2")) space:2
    space S23(("s23")) space:3 S3(("s3")) space
    S33(("s33")) space:5 S01(("s01"))
    S13(("s13")) space:2 R["Hash ring<br/>4 servers<br/>16 tokens"] space:2 S21(("s21"))
    S03(("s03")) space:5 S11(("s11"))
    space S12(("s12")) space:3 S31(("s31")) space
    space:2 S22(("s22")) S32(("s32")) S02(("s02")) space:2

    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S01
    S01 --> S21
    S21 --> S11
    S11 --> S31
    S31 --> S02
    S02 --> S32
    S32 --> S22
    S22 --> S12
    S12 --> S03
    S03 --> S13
    S13 --> S33
    S33 --> S23
    S23 --> S0

    classDef server0 fill:#b00000,stroke:#fff,color:#fff
    classDef server1 fill:#b86600,stroke:#fff,color:#fff
    classDef server2 fill:#55aa00,stroke:#fff,color:#fff
    classDef server3 fill:#073db5,stroke:#fff,color:#fff
    class S0,S01,S02,S03 server0
    class S1,S11,S12,S13 server1
    class S2,S21,S22,S23 server2
    class S3,S31,S32,S33 server3
    style R fill:transparent,stroke:transparent,color:#111
```

**Diagram:** Same-colored tokens belong to the **same physical server**, matching the color grouping in the supplied figure. All four tokens per server are shown with distinct labels. This is a schematic ring: the spacing does not represent actual hash distances, and token names are identifiers—not their numeric order. Keys lie between tokens and still go to the first clockwise token.

**Routing examples:**

| Key position on this ring | Next clockwise token | Physical destination |
| --- | --- | --- |
| Between `s3` and `s01` | `s01` | server0 |
| Between `s01` and `s21` | `s21` | server2 |
| Between `s31` and `s02` | `s02` | server0 |
| Between `s33` and `s23` | `s23` | server2 |

**If server0 is removed, all its red tokens disappear:**

- The range previously owned by `s0` goes to `s1` → **server1**.
- The range previously owned by `s01` goes to `s21` → **server2**.
- The range previously owned by `s02` goes to `s32` → **server3**.
- The range previously owned by `s03` goes to `s13` → **server1**.

Its load is therefore spread across **three surviving physical servers**, rather than pushed entirely onto one. This improves the distribution in this example; it does not guarantee perfectly equal load or prevent overload without enough spare capacity.

### Applications and Practical Limits

| Application | What consistent hashing helps decide |
| --- | --- |
| **Distributed cache** | Which cache server should hold a key, while limiting cache misses when membership changes. |
| **Distributed database** | Which node owns a partition-key range; replication and consistency rules are separate concerns. |
| **Key-based request routing** | Which backend handles a customer, session, or object key, with fewer routing changes as servers change. |
| **Content-cache layer** | Which cache holds an object in a CDN or distributed content-serving system that uses this placement scheme. |

Practical designs must also handle:

- **Membership updates:** Routers need an appropriate, coordinated view of the token map. A temporary outage need not trigger permanent removal and data migration.
- **Data movement:** Transfer ranges safely when nodes join or leave; reassignment alone does not move stored bytes.
- **Replication:** Store copies on distinct physical nodes, preferably across independent failure domains. Several vnodes on one machine are **not independent replicas**. [Cassandra's replication explanation](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html#multi-master-replication-versioned-data-and-tunable-consistency)
- **Capacity and hot keys:** More tokens can improve key distribution, but do not add CPU or memory. Higher-capacity servers can be assigned more tokens; a single hot key may still need caching or replication.
- **Overhead:** More tokens mean a larger token map and more ranges to manage during migration or repair.

> **Recall:** Consistent hashing limits **key movement**. Virtual nodes improve **range distribution**. Replication protects **data copies**. None of these alone guarantees availability, strong consistency, or perfectly balanced traffic.

**Industry C++ implementations:** [Envoy's ring-hash load balancer](https://github.com/envoyproxy/envoy/blob/main/source/extensions/load_balancing_policies/ring_hash/ring_hash_lb.cc) builds a virtual-node ring and uses binary search to select hosts. [Apache bRPC's consistent-hashing load balancer](https://github.com/apache/brpc/blob/master/src/brpc/policy/consistent_hashing_load_balancer.cpp) implements virtual nodes, membership updates, and hashing policies including Ketama. These are established framework components, not small standalone DSA procedures.

**Hands-on DSA core:** [consistent_hashing_dsa.cpp](examples/consistent_hashing/consistent_hashing_dsa.cpp) implements **AddServer**, **RemoveServer**, and **GetServer** with virtual nodes and clockwise lookup. See its [README: pseudocode, complexity, build commands, and illustrated output](examples/consistent_hashing/README.md). It is an independently written C++17 teaching example—not production-ready code or a routing-compatible replacement for Envoy/bRPC.

## Bloom Filters

**A Bloom filter** is a space-efficient, probabilistic data structure for checking whether an element belongs to a set. It stores a **bit array**, not the elements themselves.

> **Mental model:** A Bloom filter is a fast rejection gate: **“definitely not here”** or **“might be here—check the real set.”**

### How a Bloom Filter Works

The filter has:

- **m bits**, initially all 0.
- **k hash functions**, each selecting a position from `0` to `m − 1`.

**Insert an element:** Apply all k hashes and set their selected bits to 1. Multiple elements can share the same bits.

**Check an element:** Apply the **same** hashes:

- If **any selected bit is 0**, the element is **definitely absent** from the represented set.
- If **all selected bits are 1**, the element is **possibly present**. Those bits could have been set by other elements.

The result is deterministic for a fixed filter and key; *probabilistic* describes the chance that an absent key's positions happen to be occupied.

### Membership Guarantees

| Filter answer | What it means | Possible error |
| --- | --- | --- |
| **Definitely absent** | At least one required bit is 0; this key was not successfully inserted. | No false negative under the filter's operating assumptions. |
| **Possibly present** | All required bits are 1. | A **false positive**: the key may never have been inserted. |

**Why no false negatives?** Inserting a key sets all of its bits. Later insertions only set more bits; they never clear the existing ones.

This guarantee assumes completed insertions, unchanged hashes/configuration, intact bits, and correct synchronization. It describes **the set represented by the filter**, not a newer database whose updates have not reached it.

### Username Example

Suppose the existing usernames are **john, dave, and peter**, with **m = 10** bits and **k = 2** hash functions. Positions are zero-indexed.

| Username | h1 position | h2 position |
| --- | ---: | ---: |
| `john` | 5 | 8 |
| `dave` | 3 | 5 |
| `peter` | 2 | 9 |

| Step | Bit array: positions 0–9 |
| --- | --- |
| Initialize | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| Insert john: set 5 and 8 | `[0, 0, 0, 0, 0, 1, 0, 0, 1, 0]` |
| Insert dave: set 3 and 5 | `[0, 0, 0, 1, 0, 1, 0, 0, 1, 0]` |
| Insert peter: set 2 and 9 | `[0, 0, 1, 1, 0, 1, 0, 0, 1, 1]` |

Now check two proposed usernames:

| Query | Hash positions | Bits inspected | Filter answer | Actual membership |
| --- | --- | --- | --- | --- |
| **donald** | 3 and 7 | 1 and **0** | **Definitely absent** | Not in the existing set. |
| **sarah** | 3 and 8 | 1 and 1 | **Possibly present** | Not in the existing set: a **false positive**. |

**Why does sarah produce a false positive?** Dave set bit 3, and john set bit 8. Sarah's hashes select those same bits. The filter remembers only that they are set—not which usernames set them.

> The filter does **not** prove that sarah is taken; check the authoritative username store. Donald is absent from the represented set, but that does **not reserve the name**. Another user could claim it concurrently, so final registration needs an **atomic database uniqueness constraint**.

### Membership Decision Diagram

```mermaid
flowchart TB
    Q["Membership query"] --> H["Hash the key to k bit positions"]
    H --> B{"Is any selected bit 0?"}
    B -->|Yes| N["Definitely absent<br/>Skip the represented-set lookup"]
    B -->|No| M["Possibly present"]
    M --> E["Check the authoritative set<br/>when exact membership is required"]
    E --> R{"Actually present?"}
    R -->|Yes| P["Confirmed member"]
    R -->|No| F["False positive<br/>Not a member"]

    classDef step fill:#dcecff,stroke:#326ce5,color:#111
    classDef decision fill:#fff4cc,stroke:#b58a00,color:#111
    classDef absent fill:#d8f0df,stroke:#26834a,color:#111
    classDef possible fill:#ffe1d6,stroke:#b45030,color:#111
    class Q,H,E step
    class B,R decision
    class N,P absent
    class M,F possible
```

**Diagram assumption:** The filter accurately represents the set being queried. Skipping a lookup based on a stale filter can miss newer records. For username creation, neither branch replaces the database's atomic uniqueness check.

### Sizing and False-Positive Trade-Offs

Let **n** be the number of distinct inserted elements, **m** the bit count, **k** the hash count, and **p** the false-positive probability for an absent key.

Under the usual well-distributed, approximately independent hashing assumptions:

$$
p \approx \left(1-e^{-kn/m}\right)^k
$$

For a planned n and target p, useful sizing estimates are:

$$
m \approx -\frac{n\ln p}{(\ln 2)^2},
\qquad
k_{\mathrm{opt}} \approx \frac{m}{n}\ln 2
$$

Choose an integer k near the optimum. These are sizing approximations, not an exact prediction for every small filter or hash implementation. [Bloom-filter analysis](https://www.eecs.harvard.edu/~michaelm/postscripts/dimacs-chapter-08.pdf)

**Example:** To represent **1,000 distinct keys** with roughly **1% false positives**:

$$
m \approx -\frac{1000\ln(0.01)}{(\ln 2)^2}
\approx 9585\text{ bits}
$$

Round to about **9,600 bits = 1,200 bytes**, then:

$$
k_{\mathrm{opt}} \approx \frac{9600}{1000}\ln 2
\approx 6.65 \quad\Rightarrow\quad k = 7
$$

This is the bit-array budget, excluding configuration/container overhead. About 1% of **absent-key queries** may require an unnecessary exact lookup; it does not mean 1% of inserted keys disappear.

| Change | Benefit / cost |
| --- | --- |
| **Increase m at fixed n and k** | Generally fewer false positives, but more memory. |
| **Increase k toward the optimum** | Can reduce false positives, but adds hashing and bit probes. |
| **Increase k beyond the optimum** | Can increase false positives by setting too many bits, as well as increasing CPU cost. |
| **Insert more distinct elements at fixed m and k** | More bits become 1, increasing false positives; a saturated filter becomes unhelpful. |

> **More hash functions are not always better.** Size the bit array and hash count together for the expected number of distinct elements.

### Bloom Filter Applications

| Application | How the filter helps | Important qualification |
| --- | --- | --- |
| **Membership screening** | Quickly reject unseen URLs in a crawler or absent words in a dictionary. | Verify positives if exact membership matters. |
| **Cache lookup screening** | Skip an expensive cache lookup when a key is definitely absent from the represented cache contents. | Keep membership updates safe; the filter's own cost must be worthwhile. |
| **Database disk-read reduction** | Skip an SST file that definitely does not contain a key. | A positive still requires the normal lookup. RocksDB uses Bloom filters this way. |
| **Network candidate screening** | Summarize sets to narrow possible destinations or other lookup candidates. | A probabilistic match is not authoritative routing or authorization. |
| **Duplicate detection** | Identify possible repeats before an exact duplicate check. | Discarding every positive can wrongly discard a new item. |

RocksDB's filters avoid unnecessary work for absent keys; false positives add extra lookup work rather than inventing records. [RocksDB Bloom-filter documentation](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)

### Limitations and Safe Use

- **No ordinary deletion:** Clearing a bit can erase evidence shared by another key. For example, clearing dave's bit 5 makes an inserted john appear absent. Counting Bloom filters can support deletion with additional counters and careful bookkeeping.
- **No key retrieval or enumeration:** The filter stores a summary, not the original elements or values.
- **No automatic capacity growth:** A fixed filter becomes less useful as more distinct keys are inserted. Rebuild or use an appropriate growing-filter design when needed.
- **No synchronization guarantee:** A stale or incorrectly updated filter may not represent the real set. Distributed updates and concurrent access require separate safeguards.
- **No exact uniqueness or security decision:** Use authoritative checks where a false positive or stale negative would cause harm.

> **Recall:** Bloom filters save memory and avoid unnecessary lookups by tolerating **false positives**, not false negatives for correctly inserted keys. They are a **pre-filter**, not a replacement for the authoritative data store.

### DSA-Style Bloom Filter Implementation

**Hands-on C++17 core:** [bloom_filter_dsa.cpp](examples/bloom_filter/bloom_filter_dsa.cpp) implements **Insert** and **MayContain** using packed bits and seeded hashes. Its walkthrough reproduces the username example above, including sarah's false positive. See the [README: pseudocode, complexity, build commands, and exact output](examples/bloom_filter/README.md).

Insertion and worst-case lookup take **O(k)** work under constant-time hashing assumptions; string hashing in this implementation takes **O(k(L + 1))** for a key of L bytes. Storage is **m bits**, rounded to words, plus k hash seeds. The example is educational, insertion-only, and does not implement database uniqueness or distributed filter synchronization.

## Count-Min Sketch

> Study notes to be added.

## HyperLogLog

> Study notes to be added.

## References

- [Adam Kirsch, Michael Mitzenmacher, and George Varghese — Hash-Based Techniques for High-Speed Packet Processing](https://www.eecs.harvard.edu/~michaelm/postscripts/dimacs-chapter-08.pdf)
- [RocksDB — Bloom Filter Design and Database Use](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter)
- [David Karger and colleagues — Consistent Hashing and Random Trees](https://people.csail.mit.edu/karger/Papers/web.pdf)
- [Apache Cassandra — Consistent Hashing, Virtual Nodes, and Replication](https://cassandra.apache.org/doc/latest/cassandra/architecture/dynamo.html)
- [Envoy — Ring-Hash C++ Implementation](https://github.com/envoyproxy/envoy/blob/main/source/extensions/load_balancing_policies/ring_hash/ring_hash_lb.cc)
- [Apache bRPC — Consistent-Hashing C++ Implementation](https://github.com/apache/brpc/blob/master/src/brpc/policy/consistent_hashing_load_balancer.cpp)
- [Michael J. Fischer, Nancy A. Lynch, and Michael S. Paterson — Impossibility of Distributed Consensus with One Faulty Process](https://cs.nyu.edu/~apanda/classes/sp25/papers/fischer85impossibility.pdf)
- [Cynthia Dwork, Nancy Lynch, and Larry Stockmeyer — Consensus in the Presence of Partial Synchrony](https://groups.csail.mit.edu/tds/papers/Lynch/jacm88.pdf)
- [James Aspnes — Randomized Protocols for Asynchronous Consensus](https://arxiv.org/html/cs/0209014)
- [Tushar Deepak Chandra and Sam Toueg — Unreliable Failure Detectors for Reliable Distributed Systems](https://www.cs.cornell.edu/courses/cs734/2000FA/cached%20papers/ct96.pdf)
- [Seth Gilbert and Nancy Lynch — Perspectives on the CAP Theorem](https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf)
- [Eric Brewer — CAP Twelve Years Later: How the "Rules" Have Changed](https://www.infoq.com/articles/cap-twelve-years-later-how-the-rules-have-changed/)
- [Daniel Abadi — PACELC: Original Explanation](https://dbmsmusings.blogspot.com/2010/04/problems-with-cap-and-yahoos-little.html)
- [Daniel Abadi — Consistency Tradeoffs in Modern Distributed Database System Design](https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf)
- [Leslie Lamport — Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- [Leslie Lamport — Fast Paxos](https://www.microsoft.com/en-us/research/publication/fast-paxos/)
- [Diego Ongaro and John Ousterhout — In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf)
- [Google — The Chubby Lock Service](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)
- [Google — Spanner's Published Design](https://storage.googleapis.com/gweb-research2023-media/pubtools/1974.pdf)
- [Apache ZooKeeper — Administration and Zab](https://zookeeper.apache.org/doc/current/zookeeperAdmin.html)
- [Apache ZooKeeper — Internals, Atomic Broadcast, and Consistency Guarantees](https://zookeeper.apache.org/doc/current/zookeeperInternals.html)
- [Barbara Liskov and James Cowling — Viewstamped Replication Revisited](https://dspace.mit.edu/entities/publication/80846d94-fcd3-40e6-87fb-8d91fe99a5d1)
- [Iulian Moraru, David G. Andersen, and Michael Kaminsky — Egalitarian Paxos](https://www.pdl.cmu.edu/PDL-FTP/associated/epaxos-sosp2013_abs.shtml)
- [Maofan Yin and colleagues — HotStuff](https://arxiv.org/abs/1803.05069)
- [Apache Hadoop — HDFS High Availability](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html)
- [etcd — Raft Implementation](https://go.etcd.io/etcd/raft/v3)
- [HashiCorp — Consul Consensus](https://developer.hashicorp.com/consul/docs/concept/consensus)
- [Netflix — ChAP: Chaos Automation Platform](https://netflixtechblog.com/chap-chaos-automation-platform-53e6d528371f)
- [Leslie Lamport, Robert Shostak, and Marshall Pease — The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf)
- [Miguel Castro and Barbara Liskov — Practical Byzantine Fault Tolerance](https://www.usenix.org/legacy/events/osdi99/full_papers/castro/castro_html/castro.html)
- [Christian Cachin, Klaus Kursawe, and Victor Shoup — Randomized Asynchronous Byzantine Agreement](https://eprint.iacr.org/2000/034)
- [Satoshi Nakamoto — Bitcoin: A Peer-to-Peer Electronic Cash System](https://bitcoin.org/bitcoin.pdf)
- [Ethereum — Proof-of-Stake Consensus and Finality](https://ethereum.org/en/developers/docs/consensus-mechanisms/pos/)
