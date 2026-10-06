// Basic Paxos for ONE decision: small procedures, not a networked service.
// Preconditions: fixed distinct acceptors; correct participants; each new
// attempt has a globally unique number, never reused for a different proposal.
// State is in memory. Real crash recovery requires persistence before replies.
#include <cstdint>
#include <iostream>
#include <optional>
#include <vector>

namespace paxos_dsa {

struct Proposal {
    std::uint64_t number;
    int value;
};

struct Acceptor {
    std::optional<std::uint64_t> promised;
    std::optional<Proposal> accepted;
    bool available = true;
};

struct Promise {
    bool ok;
    std::optional<Proposal> accepted;
};

// Acceptor procedure: promise not to accept proposals below number.
Promise Prepare(Acceptor& node, std::uint64_t number) {
    if (!node.available || (node.promised && number < *node.promised)) {
        return {false, std::nullopt};
    }
    node.promised = number;
    return {true, node.accepted};
}

// Acceptor procedure: record acceptance before acknowledging it.
bool Accept(Acceptor& node, std::uint64_t number, int value) {
    if (!node.available || (node.promised && number < *node.promised)) {
        return false;
    }
    if (node.accepted && node.accepted->number == number &&
        node.accepted->value != value) {
        return false; // Reject conflicting reuse of a proposal number.
    }
    node.promised = number;
    node.accepted = Proposal{number, value};
    return true;
}

// Proposer procedure; the final majority check also performs the learner step.
std::optional<int> Propose(std::vector<Acceptor>& nodes,
                           std::uint64_t number, int requestedValue) {
    const std::size_t quorum = nodes.size() / 2 + 1;
    std::size_t promises = 0;
    std::optional<Proposal> highestAccepted;

    // Phase 1: prepare, count promises, and find the highest accepted proposal.
    for (auto& node : nodes) {
        const auto reply = Prepare(node, number);
        if (!reply.ok) continue;
        ++promises;
        if (reply.accepted && (!highestAccepted ||
            highestAccepted->number < reply.accepted->number)) {
            highestAccepted = reply.accepted;
        }
    }
    if (promises < quorum) return std::nullopt;

    const int value = highestAccepted ? highestAccepted->value : requestedValue;
    std::size_t acknowledgments = 0;

    // Phase 2: each distinct acceptor is visited once; no duplicate votes.
    for (auto& node : nodes) {
        if (Accept(node, number, value)) ++acknowledgments;
    }
    if (acknowledgments < quorum) return std::nullopt;
    return value; // A majority accepted this same (number, value): chosen.
}

} // namespace paxos_dsa

int main() {
    std::vector<paxos_dsa::Acceptor> nodes(3);
    for (const auto& proposal : {paxos_dsa::Proposal{1, 20},
                                paxos_dsa::Proposal{2, 5}}) {
        const auto chosen = paxos_dsa::Propose(nodes, proposal.number, proposal.value);
        std::cout << "Proposal " << proposal.number << " requests " << proposal.value << " -> ";
        if (chosen) std::cout << "chosen " << *chosen;
        else std::cout << "no decision established by this attempt";
        std::cout << '\n';
    }
    return 0;
}
