// Compact Raft core: fixed membership, correct nodes, synchronous calls, memory only.
// Node IDs are vector indices. Index 0 is a sentinel; real entries start at 1.
// No timers, disk, snapshots, membership changes, or client retry deduplication.
#include <algorithm>
#include <cstdint>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <utility>
#include <vector>

namespace raft_dsa {
using Index = std::size_t;
using Term = std::uint64_t;
enum class Role { Follower, Candidate, Leader };
struct Entry { Term term; int credit; };
struct Reply { Term term; bool ok; };
struct Node {
    Role role = Role::Follower;
    Term term = 0;
    int votedFor = -1;
    std::vector<Entry> log{{0, 0}};
    Index commitIndex = 0, lastApplied = 0;
    std::int64_t balance = 0;
    bool available = true;
    std::vector<Index> nextIndex, matchIndex; // Used only while leader.
};

void ObserveTerm(Node& node, Term term) {
    if (term > node.term) {
        node.term = term;
        node.votedFor = -1;
        node.role = Role::Follower;
    }
}

void ApplyCommitted(Node& node) {
    while (node.lastApplied < node.commitIndex) {
        node.balance += node.log[++node.lastApplied].credit;
    }
}

std::optional<Reply> RequestVote(Node& node, Term term, int candidate,
                                 Term lastTerm, Index lastIndex) {
    if (!node.available) return std::nullopt;
    ObserveTerm(node, term);
    const bool fresh = std::make_pair(lastTerm, lastIndex) >=
                       std::make_pair(node.log.back().term, node.log.size() - 1);
    const bool granted = term == node.term && fresh &&
                        (node.votedFor == -1 || node.votedFor == candidate);
    if (granted) node.votedFor = candidate; // Repeat votes never add another voter.
    return Reply{node.term, granted};
}

std::optional<Reply> AppendEntries(Node& node, Term term, Index prevIndex,
        Term prevTerm, std::optional<Entry> entry, Index leaderCommit) {
    if (!node.available) return std::nullopt;
    ObserveTerm(node, term);
    if (term < node.term) return Reply{node.term, false};
    node.role = Role::Follower;
    if (prevIndex >= node.log.size() || node.log[prevIndex].term != prevTerm) {
        return Reply{node.term, false};
    }
    const Index index = prevIndex + 1;
    if (entry) {
        if (index < node.log.size() && node.log[index].term != entry->term) {
            if (index <= node.commitIndex) throw std::logic_error("Cannot replace a committed entry");
            node.log.resize(index); // Delete conflicting entry and its suffix.
        }
        if (index == node.log.size()) node.log.push_back(*entry);
        else if (node.log[index].credit != entry->credit) {
            throw std::logic_error("Same index and term must contain the same command");
        }
    }
    // Bound commitment by the prefix verified by THIS request, not extra local entries.
    const Index verified = prevIndex + (entry ? 1 : 0);
    node.commitIndex = std::max(node.commitIndex, std::min(leaderCommit, verified));
    ApplyCommitted(node);
    return Reply{node.term, true};
}

bool Replicate(std::vector<Node>& nodes, Index leaderId) {
    auto& leader = nodes.at(leaderId);
    if (!leader.available || leader.role != Role::Leader) return false;
    const Index last = leader.log.size() - 1;
    leader.matchIndex[leaderId] = last;
    for (Index id = 0; id < nodes.size(); ++id) {
        if (id == leaderId) continue;
        while (true) {
            const Index next = leader.nextIndex[id], prev = next - 1;
            const auto entry = next <= last ? std::optional<Entry>{leader.log[next]} : std::nullopt;
            const auto reply = AppendEntries(nodes[id], leader.term, prev,
                                             leader.log[prev].term, entry, leader.commitIndex);
            if (!reply) break; // Unavailable: do not count a new acknowledgment.
            ObserveTerm(leader, reply->term);
            if (leader.role != Role::Leader) return false;
            if (!reply->ok) {
                if (next == 1) throw std::logic_error("Valid empty prefix must match");
                --leader.nextIndex[id]; // Backtrack, then resend one entry at a time.
                continue;
            }
            const Index matched = prev + (entry ? 1 : 0);
            leader.matchIndex[id] = std::max(leader.matchIndex[id], matched);
            leader.nextIndex[id] = matched + 1;
            if (matched == last) break;
        }
    }
    // Compact choice: check only the newest entry; do not commit older-term tails
    // by counting copies. A current-term tail commits the entire preceding prefix.
    const auto copies = static_cast<Index>(std::count_if(leader.matchIndex.begin(),
        leader.matchIndex.end(), [last](Index index) { return index >= last; }));
    if (last > leader.commitIndex && leader.log[last].term == leader.term &&
        copies >= nodes.size() / 2 + 1) leader.commitIndex = last;
    ApplyCommitted(leader);
    for (Index id = 0; id < nodes.size(); ++id) {
        if (id == leaderId || leader.matchIndex[id] < leader.commitIndex) continue;
        const Index prev = leader.matchIndex[id];
        const auto reply = AppendEntries(nodes[id], leader.term, prev,
            leader.log[prev].term, std::nullopt, leader.commitIndex); // Commit heartbeat.
        if (reply) ObserveTerm(leader, reply->term);
        if (leader.role != Role::Leader) return false;
    }
    return leader.commitIndex >= last;
}

bool StartElection(std::vector<Node>& nodes, Index candidateId) {
    auto& candidate = nodes.at(candidateId);
    if (!candidate.available) return false;
    ObserveTerm(candidate, candidate.term + 1);
    candidate.role = Role::Candidate;
    candidate.votedFor = static_cast<int>(candidateId);
    Index votes = 1;
    for (Index id = 0; id < nodes.size(); ++id) {
        if (id == candidateId) continue;
        const auto reply = RequestVote(nodes[id], candidate.term, static_cast<int>(candidateId),
                                       candidate.log.back().term, candidate.log.size() - 1);
        if (!reply) continue;
        ObserveTerm(candidate, reply->term);
        if (candidate.role != Role::Candidate) return false;
        if (reply->ok) ++votes; // Each distinct node is visited only once.
    }
    if (votes < nodes.size() / 2 + 1) return false;
    candidate.role = Role::Leader;
    candidate.nextIndex.assign(nodes.size(), candidate.log.size());
    candidate.matchIndex.assign(nodes.size(), 0);
    Replicate(nodes, candidateId); // Initial heartbeat; may also repair follower logs.
    return candidate.role == Role::Leader;
}

bool Submit(std::vector<Node>& nodes, Index leaderId, int credit) {
    auto& leader = nodes.at(leaderId);
    if (!leader.available || leader.role != Role::Leader) return false;
    leader.log.push_back({leader.term, credit});
    return Replicate(nodes, leaderId);
}
} // namespace raft_dsa

int main() {
    std::vector<raft_dsa::Node> nodes(3);
    if (!raft_dsa::StartElection(nodes, 0)) return 1;
    std::cout << "An elected leader in term " << nodes[0].term << '\n';
    for (int credit : {20, 5}) {
        const bool committed = raft_dsa::Submit(nodes, 0, credit);
        std::cout << "Entry " << nodes[0].log.size() - 1 << ": credit " << credit << " -> "
                  << (committed ? "committed" : "not confirmed")
                  << "; balance " << nodes[0].balance << '\n';
        if (!committed) return 1;
    }
    return 0;
}
