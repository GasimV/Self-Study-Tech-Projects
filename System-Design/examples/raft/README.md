# DSA-Style Raft in C++17

Raft elects a leader and agrees on an **ordered log of commands**. This example separates the algorithm into short procedures, with matching pseudocode and a small runnable demonstration.

> [raft_dsa.cpp](raft_dsa.cpp) is a synchronous, memory-only learning core, not a production distributed service. It models three fixed nodes and explicitly triggered elections. The [original Raft paper](https://raft.github.io/raft.pdf) describes the full protocol.

## Table of Contents

- [Build and Run](#build-and-run)
- [Roles, State, and Procedures](#roles-state-and-procedures)
- [Language-Neutral Pseudocode](#language-neutral-pseudocode)
- [Illustrated Input and Output](#illustrated-input-and-output)
- [Complexity Breakdown](#complexity-breakdown)
- [Safety Rules to Remember](#safety-rules-to-remember)
- [Assumptions and Limits](#assumptions-and-limits)
- [Verification](#verification)
- [References](#references)

## Build and Run

From the **repository root**, with a C++17 compiler on your `PATH`:

```powershell
.\examples\raft\build.cmd
.\examples\raft\raft_dsa.exe
```

The script creates `examples/raft/raft_dsa.exe`, regardless of your current directory. From inside `examples/raft`, use `.\build.cmd` and `.\raft_dsa.exe`. It works from PowerShell or Command Prompt without changing execution policies. Unsupported build arguments print usage and fail.

Direct compilation:

```powershell
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/raft/raft_dsa.cpp -o examples/raft/raft_dsa.exe
```

Linux/macOS:

```sh
g++ -std=c++17 -Wall -Wextra -Wpedantic examples/raft/raft_dsa.cpp -o examples/raft/raft_dsa
./examples/raft/raft_dsa
```

No external libraries or build system are needed. Generated executables are ignored by the folder's `.gitignore`. The program takes no scenario arguments; its small `main()` supplies the demonstration inputs.

## Roles, State, and Procedures

| Role | Responsibility |
| --- | --- |
| **Follower** | Respond to vote and replication requests. |
| **Candidate** | Request votes for a new term. |
| **Leader** | Append client commands, replicate them, and announce commitment. |

A node's **term** is an election-era number, not a money amount or log position. A **log index** identifies a command's position; multiple entries can belong to the same term.

| Node state | Meaning |
| --- | --- |
| `role`, `term` | Current role and highest term observed. |
| `votedFor` | Candidate voted for in this term; `-1` means none. |
| `log` | Entries containing a term and an integer `credit` command. |
| `commitIndex` | Highest position known to be committed. |
| `lastApplied` | Highest committed position already applied. |
| `balance` | Toy state-machine result: sum of applied credits. |
| `available` | Whether synchronous requests receive replies from this node. |
| `nextIndex[f]` | Leader's next log position to send to follower `f`. |
| `matchIndex[f]` | Highest position the leader knows follower `f` has replicated. |

Node IDs are vector indices: **0 = A, 1 = B, 2 = C**. Log position **0** is a sentinel `(term 0, credit 0)`; real commands begin at **1**. Membership is fixed, and a majority is **2 of 3**, even when a node is unavailable.

| Procedure | Work performed |
| --- | --- |
| `ObserveTerm` | Discovering a higher term resets the vote and changes the node to follower. |
| `RequestVote` | Grant a vote only in the current term, to an eligible candidate with a sufficiently fresh log. |
| `StartElection` | Increment the term, self-vote, collect a majority, initialize leader progress, and send an initial replication/heartbeat pass. |
| `AppendEntries` | Verify the preceding entry, record an optional new entry, and apply the verified committed prefix. |
| `Replicate` | Backtrack and send entries until followers catch up; establish commitment and send commit heartbeats. |
| `Submit` | Append one client command to the leader's log, then replicate it. |
| `ApplyCommitted` | Apply each committed command once, in order. |

## Language-Neutral Pseudocode

`NO_REPLY` represents an unavailable node. Otherwise, a reply contains the node's current term and a Boolean result. All loops visit **distinct configured nodes**, not arbitrary repeated replies.

```text
OBSERVE_TERM(node, term):
    if term > node.term:
        node.term = term
        node.votedFor = NONE
        node.role = FOLLOWER

APPLY_COMMITTED(node):
    while node.lastApplied < node.commitIndex:
        node.lastApplied = node.lastApplied + 1
        node.balance = node.balance + node.log[node.lastApplied].credit

REQUEST_VOTE(node, term, candidateId, lastTerm, lastIndex):
    if not node.available: return NO_REPLY
    OBSERVE_TERM(node, term)
    fresh = (lastTerm, lastIndex) >= (node.log.last.term, node.log.lastIndex)
    granted = term == node.term and fresh and
              (node.votedFor == NONE or node.votedFor == candidateId)
    if granted: node.votedFor = candidateId
    return (node.term, granted)

APPEND_ENTRIES(node, term, prevIndex, prevTerm, optionalEntry, leaderCommit):
    if not node.available: return NO_REPLY
    OBSERVE_TERM(node, term)
    if term < node.term: return (node.term, false)
    node.role = FOLLOWER
    if prevIndex is missing or node.log[prevIndex].term != prevTerm:
        return (node.term, false)

    index = prevIndex + 1
    if optionalEntry exists:
        if index exists and node.log[index].term != optionalEntry.term:
            require index > node.commitIndex
            delete entries from index onward
        if index is missing: append optionalEntry
        else: require existing command == optionalEntry.command

    verified = prevIndex + (1 if optionalEntry exists else 0)
    node.commitIndex = max(node.commitIndex, min(leaderCommit, verified))
    APPLY_COMMITTED(node)
    return (node.term, true)

START_ELECTION(nodes, candidateId):
    candidate = nodes[candidateId]
    if not candidate.available: return false
    OBSERVE_TERM(candidate, candidate.term + 1)
    candidate.role = CANDIDATE
    candidate.votedFor = candidateId
    votes = 1
    for each other node:
        reply = REQUEST_VOTE(node, candidate.term, candidateId,
                             candidate.log.last.term, candidate.log.lastIndex)
        if reply == NO_REPLY: continue
        OBSERVE_TERM(candidate, reply.term)
        if candidate.role != CANDIDATE: return false
        if reply.granted: votes = votes + 1
    if votes < majority(length(nodes)): return false
    candidate.role = LEADER
    nextIndex for each node = candidate.log.lastIndex + 1
    matchIndex for each node = 0
    REPLICATE(nodes, candidateId)
    return candidate.role == LEADER

REPLICATE(nodes, leaderId):
    leader = nodes[leaderId]
    if not leader.available or leader.role != LEADER: return false
    last = leader.log.lastIndex
    leader.matchIndex[leaderId] = last

    for each follower f:
        repeat:
            next = leader.nextIndex[f]
            prev = next - 1
            entry = leader.log[next] if next <= last, otherwise NONE
            reply = APPEND_ENTRIES(f, leader.term, prev, leader.log[prev].term,
                                   entry, leader.commitIndex)
            if reply == NO_REPLY: stop this follower's attempt
            OBSERVE_TERM(leader, reply.term)
            if leader.role != LEADER: return false
            if not reply.success:
                require next > 1
                leader.nextIndex[f] = next - 1
                continue
            matched = prev + (1 if entry exists else 0)
            leader.matchIndex[f] = max(leader.matchIndex[f], matched)
            leader.nextIndex[f] = matched + 1
            if matched == last: stop this follower's attempt

    copies = number of nodes with leader.matchIndex[node] >= last
    if last > leader.commitIndex and leader.log[last].term == leader.term
       and copies >= majority(length(nodes)):
        leader.commitIndex = last
    APPLY_COMMITTED(leader)

    for each follower f with leader.matchIndex[f] >= leader.commitIndex:
        prev = leader.matchIndex[f]
        send APPEND_ENTRIES(f, leader.term, prev, leader.log[prev].term,
                            NONE, leader.commitIndex)
        observe any returned higher term; if no longer leader, return false
    return leader.commitIndex >= last

SUBMIT(nodes, leaderId, credit):
    leader = nodes[leaderId]
    if not leader.available or leader.role != LEADER: return false
    append (leader.term, credit) to leader.log
    return REPLICATE(nodes, leaderId)
```

Log freshness compares **last term first, then last index**. A longer log is not automatically fresher if its last term is lower. `AppendEntries` sends at most one new entry; an empty request is a **heartbeat**, which can also carry the commit position.

## Illustrated Input and Output

The inputs supplied by `main()` are:

1. Create A, B, and C with empty logs and term 0.
2. Explicitly start an election at A; A's new term is 1.
3. Submit a `credit 20` command to A.
4. Submit a separate `credit 5` command to A.

```text
A elected leader in term 1
Entry 1: credit 20 -> committed; balance 20
Entry 2: credit 5 -> committed; balance 25
```

| Committed log position | Term | Command | Balance after application |
| ---: | ---: | --- | ---: |
| 1 | 1 | `credit 20` | 20 |
| 2 | 1 | `credit 5` | 25 |

After successful replication and commit notification, each node has applied these entries in the same order. `lastApplied` prevents applying either entry again when another heartbeat arrives.

> **Both credits are processed.** They occupy two different log positions. In the Basic Paxos example, 20 and 5 competed for **one decision**, so choosing 20 prevented choosing 5 for that same decision. Raft manages an ordered sequence of decisions.

## Complexity Breakdown

Let **N** be the number of configured nodes, **L** the maximum log length across them, **K** the number of entries newly applied by a call, and **D** the number of conflicting suffix entries deleted. Commands and terms have constant size. Exclude the sentinel from L.

| Operation / resource | Cost in this implementation |
| --- | --- |
| `ObserveTerm` / `RequestVote` | O(1) local work and auxiliary space. |
| Vote collection and leader-progress initialization | O(N) work; O(N) request/reply messages in a network equivalent. |
| `AppendEntries` | O(1) amortized for a normal single-entry update, plus O(D + K) if deleting a suffix and applying a backlog. A vector growth can individually cost O(L). |
| `ApplyCommitted` | O(K) work, O(1) auxiliary space; each entry is applied once per node. |
| `Submit` / `Replicate`, caught-up followers | O(N) amortized work and messages for one new command, including commit heartbeats. |
| Backtracking and catch-up | O(1 + L) requests per follower in this fixed, synchronous setting; O(N(1 + L)) worst-case work/messages across the group, including backlog application—O(NL) for nonempty logs. |
| Logs across the group | O(NL) storage. |
| Leader progress arrays | O(N) per node that has been leader; the core retains these allocated arrays after role changes. |

`StartElection` also calls `Replicate`: its **voting part** is O(N), but the following repair pass can cost O(NL) if logs differ. The replication procedure sends one entry per request, so catch-up has more messages than a batched implementation.

For an established leader with caught-up followers, a new command needs one replication request/reply phase to establish majority storage; this implementation then sends a commit heartbeat phase so followers apply it before the demonstration returns.

> **O(N) work is not a network-latency guarantee.** The program makes local synchronous calls. Real delays, repeated elections, and retries can prevent completion for an unbounded time; the finite catch-up bound above assumes a stable leader and the available nodes returning replies.

## Safety Rules to Remember

- **Vote once per term:** a repeated request from the same candidate can repeat the reply, but it is not another voter. Election collection visits each node once.
- **Prefer fresh logs:** a candidate with an outdated log cannot win the votes needed to discard committed history.
- **Higher term means step down:** requests and replies can reveal that an old leader or candidate is outdated.
- **Check the prefix:** an entry must follow the matching previous index and term. A mismatch makes the leader backtrack and retry.
- **Do not replace committed entries:** suffix repair only replaces conflicting uncommitted entries. A heartbeat alone does not delete an extra local suffix.
- **Commit current-term entries by majority:** storing an older-term entry on a majority is not enough to newly commit it by counting copies. Committing a current-term entry commits its preceding prefix too.
- **Apply only committed entries:** storing a command is not permission to execute it. Commit notification is limited to the prefix verified by that request.

## Assumptions and Limits

- Three fixed, distinct nodes; IDs are their vector indices. The procedures also work with other nonempty fixed group sizes, but the demonstration uses three.
- Correct participants and valid Raft-generated histories. Defensive exceptions flag committed-entry replacement or different commands at the same index and term; they do not provide Byzantine fault tolerance.
- One operation runs at a time. Elections are explicitly triggered; there are no real timers, random timeouts, threads, network packets, or asynchronous response queues.
- Unavailable nodes retain their objects and state, but do not reply. This is not a disk-backed crash/restart implementation or a directed network-partition simulator.
- `Replicate` checks **only the newest log position** for new commitment. Full Raft can advance to other eligible positions as acknowledgments arrive; this compact version may wait longer if its newest entry lacks a quorum.
- No automatic no-op after election. A new leader with an uncommitted older-term tail leaves it uncommitted until a current-term entry gets a majority. `Submit` supplies such an entry in the demonstration.
- No persistent storage, snapshots, membership changes, client-request deduplication, or linearizable read protocol. The balance is a toy integer state machine, not a complete financial system.

`Submit` returning `false` does **not** roll back its appended entry or prove that the command can never commit. Call `Replicate` to retry an existing pending log entry; blindly calling `Submit` again appends another command. Application-level request IDs are needed to deduplicate real client retries.

## Verification

The core compiled with C++17 and warnings treated as errors, and the small executable reproduced the documented output. A **separate temporary test harness** compiled successfully, but Windows application control blocked its execution. Its additional protocol checks are therefore **not runtime-verified** in this environment; no policy was changed to run it.

The harness is not embedded in the core or exposed as a `--self-test` command. Its prepared checks cover:

- Majority elections, repeated votes, stale terms, higher-term step-down, and candidate log freshness.
- Replication with an unavailable node, lack of a majority, and later catch-up.
- Previous-index/term checks and repair of conflicting uncommitted suffixes.
- No new majority-count commitment of older-term entries; a current-term entry commits the preceding prefix.
- Ordered application, repeated heartbeats without double application, and commitment bounded by the verified prefix.

These are finite checks, not a proof of every asynchronous Raft execution. The existing Paxos files remain separate and unchanged.

## References

- [Raft study notes](../../Distributed-Systems-Theorems-and-Data-Structures.md#raft)
- [Diego Ongaro and John Ousterhout — In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf)
- [Compact Basic Paxos comparison](../paxos/README.md#dsa-style-paxos-core)
