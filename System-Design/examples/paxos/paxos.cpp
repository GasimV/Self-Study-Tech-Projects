// Educational single-value Paxos. All roles live in one process; no disk or network.
// Protocol reference: https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
#include <array>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <map>
#include <optional>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <tuple>
#include <utility>
#include <vector>

namespace paxos {

constexpr std::size_t kAcceptorCount = 3;
constexpr std::size_t kQuorum = kAcceptorCount / 2 + 1;
const std::string kUser1 = "book r1 for u1";
const std::string kUser2 = "book r1 for u2";

bool isMember(int id) { return id >= 1 && id <= static_cast<int>(kAcceptorCount); }

struct ProposalId {
    std::uint64_t counter;
    int proposer;

    bool operator<(const ProposalId& other) const {
        return std::tie(counter, proposer) < std::tie(other.counter, other.proposer);
    }
    bool operator==(const ProposalId& other) const {
        return counter == other.counter && proposer == other.proposer;
    }
};

std::ostream& operator<<(std::ostream& out, const ProposalId& id) {
    return out << '(' << id.counter << ",P" << id.proposer << ')';
}

struct Proposal {
    ProposalId id;
    std::string value;
};

// A reply identifies its sender AND the request it answers. Stale replies must
// not be mixed into a newer attempt, and duplicate senders count only once.
struct PromiseReply {
    int acceptor;
    ProposalId request;
    bool promised;
    std::optional<ProposalId> highestPromise;
    std::optional<Proposal> accepted;
};

struct AcceptReply {
    int acceptor;
    Proposal request;
    bool accepted;
    std::optional<ProposalId> highestPromise;
};

class Acceptor {
public:
    explicit Acceptor(int id) : id_(id) {
        if (!isMember(id)) throw std::invalid_argument("Unknown acceptor ID");
    }

    PromiseReply onPrepare(ProposalId id) {
        // Equal IDs are retries: repeat the promise and report current state.
        if (promised_ && id < *promised_) {
            return {id_, id, false, promised_, accepted_};
        }
        promised_ = id;
        return {id_, id, true, promised_, accepted_};
    }

    AcceptReply onAccept(const Proposal& proposal) {
        if (promised_ && proposal.id < *promised_) {
            return {id_, proposal, false, promised_};
        }
        // A correct proposer never sends two values with the same ID. Detect
        // this local misuse rather than overwriting a previous acceptance.
        if (accepted_ && accepted_->id == proposal.id &&
            accepted_->value != proposal.value) {
            throw std::logic_error("Proposal ID reused for a different value");
        }
        // A real crash-recoverable acceptor must persist BOTH fields before ACK.
        promised_ = proposal.id;
        accepted_ = proposal;
        return {id_, proposal, true, promised_};
    }

    int id() const { return id_; }
    const std::optional<ProposalId>& promised() const { return promised_; }
    const std::optional<Proposal>& accepted() const { return accepted_; }
    bool available = true; // Simulation transport flag; protocol state survives.

private:
    int id_;
    std::optional<ProposalId> promised_;
    std::optional<Proposal> accepted_;
};

class Proposer {
public:
    explicit Proposer(int id) : id_(id) {
        if (id < 1) throw std::invalid_argument("Proposer IDs must be positive");
    }

    void begin(std::uint64_t counter, std::string value) {
        // One persistent proposer object owns its IDs in this simulation.
        if (attempt_ && counter <= attempt_->counter) {
            throw std::logic_error("A new attempt needs a larger counter");
        }
        attempt_ = ProposalId{counter, id_};
        requested_ = std::move(value);
        promises_.clear();
        selected_.reset();
        inherited_ = false;
    }

    void onPromise(const PromiseReply& reply) {
        if (!attempt_ || !(reply.request == *attempt_) || !reply.promised ||
            !isMember(reply.acceptor) || selected_) return;
        promises_.emplace(reply.acceptor, reply); // Duplicate sender: no new vote.
    }

    std::optional<Proposal> selectValue() {
        if (selected_) return selected_; // Freeze value for this proposal ID.
        if (promises_.size() < kQuorum) return std::nullopt;
        std::optional<Proposal> highestAccepted;
        for (const auto& entry : promises_) {
            const auto& prior = entry.second.accepted;
            if (prior && (!highestAccepted || highestAccepted->id < prior->id)) {
                highestAccepted = prior;
            }
        }
        inherited_ = highestAccepted.has_value();
        selected_ = Proposal{*attempt_, highestAccepted ? highestAccepted->value : requested_};
        return selected_;
    }

    ProposalId attempt() const {
        if (!attempt_) throw std::logic_error("No proposal attempt started");
        return *attempt_;
    }
    const std::optional<Proposal>& selected() const { return selected_; }
    const std::string& requested() const { return requested_; }
    std::size_t promiseCount() const { return promises_.size(); }
    bool inherited() const { return inherited_; }

private:
    int id_;
    std::optional<ProposalId> attempt_;
    std::string requested_;
    std::map<int, PromiseReply> promises_;
    std::optional<Proposal> selected_;
    bool inherited_ = false;
};

class Learner {
public:
    void onAccepted(const AcceptReply& reply) {
        // In this simulation replies come directly from the acceptor handlers.
        // No authentication or Byzantine-fault handling is modeled.
        if (!reply.accepted || !isMember(reply.acceptor)) return;
        const auto& proposal = reply.request;
        auto [it, inserted] = evidence_.try_emplace(proposal.id, Evidence{proposal.value, {}});
        (void)inserted;
        if (it->second.value != proposal.value) {
            throw std::logic_error("Conflicting values for one proposal ID");
        }
        it->second.acceptors.insert(reply.acceptor);
        if (it->second.acceptors.size() >= kQuorum) {
            if (learned_ && *learned_ != proposal.value) {
                throw std::logic_error("Safety violation: conflicting chosen values");
            }
            learned_ = proposal.value;
        }
    }

    std::size_t ackCount(ProposalId id) const {
        const auto it = evidence_.find(id);
        return it == evidence_.end() ? 0 : it->second.acceptors.size();
    }
    const std::optional<std::string>& learned() const { return learned_; }

private:
    struct Evidence {
        std::string value;
        std::set<int> acceptors;
    };
    std::map<ProposalId, Evidence> evidence_;
    std::optional<std::string> learned_;
};

class Simulation {
public:
    explicit Simulation(std::ostream& out) : out_(out) {}
    std::array<Acceptor, kAcceptorCount> acceptors{Acceptor{1}, Acceptor{2}, Acceptor{3}};
    Proposer p1{1};
    Proposer p2{2};
    Learner learner;

    Acceptor& node(int id) {
        if (!isMember(id)) throw std::invalid_argument("Unknown acceptor ID");
        return acceptors.at(static_cast<std::size_t>(id - 1));
    }

    void start(Proposer& proposer, std::uint64_t counter, const std::string& value) {
        proposer.begin(counter, value);
        out_ << "\nINPUT: P" << proposer.attempt().proposer << " proposes " << std::quoted(value) << '\n';
    }

    bool prepare(Proposer& proposer, const std::vector<int>& targets = {1, 2, 3}) {
        const auto id = proposer.attempt();
        out_ << "PREPARE " << id << '\n';
        for (int target : targets) {
            auto& acceptor = node(target);
            out_ << "  A" << target << ": ";
            if (!acceptor.available) {
                out_ << "UNAVAILABLE (no reply)\n";
                continue;
            }
            const auto reply = acceptor.onPrepare(id);
            proposer.onPromise(reply);
            if (!reply.promised) {
                out_ << "REJECTED; promised " << *reply.highestPromise << '\n';
            } else if (reply.accepted) {
                out_ << "PROMISE; previously accepted " << reply.accepted->id << ", "
                     << std::quoted(reply.accepted->value) << '\n';
            } else {
                out_ << "PROMISE; no previously accepted value\n";
            }
        }
        out_ << "PROMISES: " << proposer.promiseCount() << '/' << kAcceptorCount
             << "; " << kQuorum << " required.\n";
        const auto selected = proposer.selectValue();
        if (!selected) {
            out_ << "RESULT: NO QUORUM - this attempt cannot enter the accept phase.\n";
            return false;
        }
        out_ << "SELECT: " << std::quoted(selected->value) << '\n'
             << "REASON: " << (proposer.inherited()
                 ? "Preserve the highest accepted value in the promise quorum."
                 : "No prior acceptance in the promise quorum; use the requested value.") << '\n';
        if (selected->value != proposer.requested()) {
            out_ << 'P' << id.proposer << "'s requested value was not selected.\n";
        }
        return true;
    }

    bool accept(Proposer& proposer, const std::vector<int>& targets = {1, 2, 3}) {
        if (!proposer.selected()) throw std::logic_error("Accept requires a promise quorum");
        const auto& proposal = *proposer.selected();
        out_ << "ACCEPT " << proposal.id << ", " << std::quoted(proposal.value) << '\n';
        for (int target : targets) {
            auto& acceptor = node(target);
            out_ << "  A" << target << ": ";
            if (!acceptor.available) {
                out_ << "UNAVAILABLE (no reply)\n";
                continue;
            }
            const auto reply = acceptor.onAccept(proposal);
            learner.onAccepted(reply);
            if (reply.accepted) out_ << "ACCEPTED\n";
            else out_ << "REJECTED; promised " << *reply.highestPromise << '\n';
        }
        const auto count = learner.ackCount(proposal.id);
        out_ << "ACKNOWLEDGMENTS: " << count << '/' << kAcceptorCount
             << "; " << kQuorum << " required.\n";
        if (count >= kQuorum) {
            out_ << "RESULT: CHOSEN " << std::quoted(proposal.value) << '\n'
                 << "LEARNER: matching majority evidence received; decision learned.\n";
            return true;
        }
        out_ << "RESULT: NO QUORUM - no decision learned from this attempt's replies.\n"
             << "This does not prove that no earlier or unobserved decision exists.\n";
        return false;
    }

    bool propose(Proposer& proposer, std::uint64_t counter, const std::string& value) {
        start(proposer, counter, value);
        return prepare(proposer) && accept(proposer);
    }

    void finalState() {
        out_ << "\nFINAL ACCEPTOR STATE\n"
             << "Node | Available | Highest promise | Accepted proposal | Accepted value\n";
        for (const auto& acceptor : acceptors) {
            out_ << 'A' << acceptor.id() << "   | " << (acceptor.available ? "yes" : "no") << " | ";
            if (acceptor.promised()) out_ << *acceptor.promised();
            else out_ << "none";
            out_ << " | ";
            if (acceptor.accepted()) {
                out_ << acceptor.accepted()->id << " | " << std::quoted(acceptor.accepted()->value);
            } else out_ << "none | none";
            out_ << '\n';
        }
        out_ << "LEARNED VALUE: ";
        if (learner.learned()) out_ << std::quoted(*learner.learned());
        else out_ << "none (absence of learning is not proof of absence of a decision)";
        out_ << '\n';
    }

private:
    std::ostream& out_;
};

const std::vector<std::string> kScenarios{
    "basic", "preserve", "one-down", "no-quorum", "preempted", "partial-accept"
};

void runScenario(const std::string& name, Simulation& sim, std::ostream& out) {
    out << "SCENARIO: " << name << "\nACCEPTORS: A1, A2, A3\nMAJORITY: " << kQuorum << '\n';
    if (name == "basic") {
        sim.propose(sim.p1, 1, kUser1);
    } else if (name == "preserve") {
        sim.propose(sim.p1, 1, kUser1);
        out << "\nPREVIOUSLY CHOSEN: " << std::quoted(*sim.learner.learned()) << '\n';
        sim.propose(sim.p2, 2, kUser2);
    } else if (name == "one-down") {
        sim.node(3).available = false;
        out << "UNAVAILABLE: A3\n";
        sim.propose(sim.p1, 1, kUser1);
    } else if (name == "no-quorum") {
        sim.node(2).available = sim.node(3).available = false;
        out << "UNAVAILABLE: A2, A3\n";
        sim.propose(sim.p1, 1, kUser1);
    } else if (name == "preempted") {
        sim.start(sim.p1, 1, kUser1);
        sim.prepare(sim.p1);
        out << "\nINTERLEAVING: P2 prepares a higher ID before P1 sends ACCEPT.\n";
        sim.start(sim.p2, 2, kUser2);
        sim.prepare(sim.p2);
        sim.accept(sim.p1);
        sim.accept(sim.p2);
    } else if (name == "partial-accept") {
        sim.start(sim.p1, 1, kUser1);
        sim.prepare(sim.p1);
        out << "DELIVERY: Only A1 receives this ACCEPT request.\n";
        sim.accept(sim.p1, {1});
        out << "\nA1 accepted, but one acceptance is not a chosen value.\n"
            << "P2's promise quorum includes A1, so P2 must carry its value forward.\n";
        sim.propose(sim.p2, 2, kUser2);
    } else throw std::invalid_argument("Unknown scenario: " + name);
    sim.finalState();
}

// Always-active checks: unlike the assert macro, these also work with -DNDEBUG.
void check(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error("Test failed: " + message);
}

template <typename Action>
void expectLogicError(Action action, const std::string& message) {
    bool threw = false;
    try { action(); } catch (const std::logic_error&) { threw = true; }
    check(threw, message);
}

void selfTest(std::ostream& out) {
    for (const auto& name : kScenarios) {
        std::ostringstream trace;
        Simulation sim(trace);
        runScenario(name, sim, trace);
        if (name == "no-quorum") {
            check(!sim.learner.learned(), "no quorum must not learn a value");
            for (const auto& node : sim.acceptors) {
                check(!node.accepted(), "prepare failure must not issue accept requests");
            }
        } else {
            const auto& expected = name == "preempted" ? kUser2 : kUser1;
            check(sim.learner.learned() == std::optional<std::string>{expected}, name + " decision");
            check(sim.learner.ackCount(name == "preserve" || name == "preempted" || name == "partial-accept"
                ? ProposalId{2, 2} : ProposalId{1, 1}) >= kQuorum, name + " majority evidence");
        }
        if (name == "one-down") check(!sim.node(3).accepted(), "unavailable node receives no accept");
        if (name == "partial-accept") {
            check(sim.learner.ackCount({1, 1}) == 1, "partial acceptance is not chosen");
            check(sim.p2.inherited(), "partial acceptance must be carried forward when observed");
        }
        if (name == "preempted") check(sim.learner.ackCount({1, 1}) == 0, "preempted accept rejected");
        out << "PASS scenario: " << name << '\n';
    }

    {
        Acceptor a1(1), a2(2);
        Proposer proposer(1);
        proposer.begin(1, "alpha");
        auto promise = a1.onPrepare(proposer.attempt());
        proposer.onPromise(promise);
        proposer.onPromise(a1.onPrepare(proposer.attempt()));
        check(proposer.promiseCount() == 1 && !proposer.selectValue(), "duplicate promises not a quorum");
        proposer.onPromise({99, proposer.attempt(), true, proposer.attempt(), std::nullopt});
        check(proposer.promiseCount() == 1, "nonmember promise excluded");
        proposer.onPromise(a2.onPrepare(proposer.attempt()));
        const auto proposal = proposer.selectValue();
        check(proposal.has_value(), "two distinct promises are a quorum");
        Learner learner;
        const auto ack = a1.onAccept(*proposal);
        learner.onAccepted(ack);
        learner.onAccepted(a1.onAccept(*proposal));
        check(learner.ackCount(proposal->id) == 1 && !learner.learned(), "duplicate ACKs not a quorum");
        auto outsider = ack;
        outsider.acceptor = 99;
        learner.onAccepted(outsider);
        check(!learner.learned(), "nonmember ACK excluded");
        const auto secondAck = a2.onAccept(*proposal);
        check(!learner.learned(), "value chosen at acceptors but not learned before second ACK delivery");
        learner.onAccepted(secondAck);
        check(learner.learned() == std::optional<std::string>{"alpha"}, "learn after actual majority evidence");
        expectLogicError([&] { proposer.begin(1, "beta"); }, "proposer must not reuse ID");
        expectLogicError([&] { a1.onAccept({proposal->id, "beta"}); }, "acceptor detects conflicting reuse");
        proposer.begin(2, "beta");
        proposer.onPromise(promise);
        check(proposer.promiseCount() == 0, "stale replies excluded from new attempt");
        check(proposer.selectValue() == std::nullopt, "cannot select without fresh quorum");
        check(!a1.onPrepare({0, 1}).promised, "old prepare rejected");
        check(!a1.onAccept({{0, 1}, "beta"}).accepted, "old accept rejected");
        out << "PASS duplicates, membership, delayed learning, ID reuse, stale replies, old requests\n";
    }

    {
        // Two different values can be accepted without either being chosen.
        // The next proposer must use the higher accepted ID, not the first reply.
        std::ostringstream trace;
        Simulation sim(trace);
        sim.start(sim.p1, 1, "alpha");
        check(sim.prepare(sim.p1), "first prepare quorum");
        check(!sim.accept(sim.p1, {1}), "alpha accepted at A1 only");
        sim.start(sim.p2, 2, "beta");
        check(sim.prepare(sim.p2, {2, 3}), "disjoint from A1, but majority prepare");
        check(!sim.accept(sim.p2, {2}), "beta accepted at A2 only");
        sim.start(sim.p1, 3, "gamma");
        check(sim.prepare(sim.p1), "recovery prepare quorum");
        check(sim.p1.selected()->value == "beta", "select highest accepted ID, not first reply");
        check(sim.accept(sim.p1), "recovery chooses beta");
        sim.propose(sim.p2, 4, "delta");
        sim.propose(sim.p1, 5, "epsilon");
        check(sim.learner.learned() == std::optional<std::string>{"beta"}, "chosen value survives later attempts");
        out << "PASS highest-accepted selection, repeated decision preservation\n";
    }

    {
        std::ostringstream trace;
        Simulation sim(trace);
        sim.start(sim.p1, 1, "alpha");
        sim.prepare(sim.p1);
        sim.accept(sim.p1, {1});
        sim.start(sim.p2, 2, "beta");
        sim.prepare(sim.p2, {2, 3});
        sim.accept(sim.p2, {3});
        sim.start(sim.p1, 3, "gamma");
        sim.prepare(sim.p1, {1, 2});
        check(sim.p1.selected()->value == "alpha", "initial quorum selects alpha");
        // A legitimate late reply reports a HIGHER previously accepted value.
        // It must not change a selection already fixed for this proposal ID.
        sim.p1.onPromise(sim.node(3).onPrepare(sim.p1.attempt()));
        check(sim.p1.selectValue()->value == "alpha", "late reply cannot change frozen selection");
        check(sim.accept(sim.p1), "fixed selection can be chosen");
        out << "PASS frozen selection despite late higher-accepted reply\n";
    }

    {
        std::ostringstream trace;
        Simulation sim(trace);
        sim.start(sim.p1, 1, "alpha");
        sim.prepare(sim.p1);
        sim.node(2).available = sim.node(3).available = false;
        check(!sim.accept(sim.p1), "losing majority between phases blocks learning");
        check(sim.learner.ackCount({1, 1}) == 1, "one phase-two ACK is not a majority");
        sim.node(2).available = sim.node(3).available = true;
        check(sim.accept(sim.p1), "retry same accept after availability returns");
        check(sim.learner.ackCount({1, 1}) == 3, "retried A1 counts once");
        sim.node(2).available = sim.node(3).available = false;
        check(!sim.propose(sim.p2, 2, "beta"), "later failed prepare cannot change earlier decision");
        check(sim.learner.learned() == std::optional<std::string>{"alpha"}, "no quorum does not erase decision");
        sim.node(2).available = sim.node(3).available = true;
        sim.start(sim.p2, 3, "beta");
        check(sim.prepare(sim.p2, {2, 3}), "different promise quorum reaches old decision");
        check(sim.accept(sim.p2, {2, 3}), "different accept quorum preserves alpha");
        check(sim.learner.learned() == std::optional<std::string>{"alpha"}, "intersecting quorums preserve decision");
        out << "PASS between-phase failures, accept retry, prior decision after no quorum, different quorums\n";
    }

    {
        check(ProposalId{1, 1} < ProposalId{1, 2}, "proposer ID breaks counter ties");
        check(ProposalId{1, 2} < ProposalId{2, 1}, "counter precedes proposer ID");
        Acceptor acceptor(1);
        acceptor.onPrepare({1, 2});
        check(!acceptor.onPrepare({1, 1}).promised, "equal-counter lower proposer rejected");
        check(acceptor.onPrepare({1, 2}).promised, "equal-ID prepare is idempotent");
        out << "PASS lexicographic proposal ordering\n";
    }
    out << "ALL TESTS PASSED\n";
}

void usage(std::ostream& out) {
    out << "Usage:\n  paxos --scenario <name>\n  paxos --self-test\n  paxos --help\nScenarios:";
    for (const auto& name : kScenarios) out << ' ' << name;
    out << '\n';
}

} // namespace paxos

int main(int argc, char* argv[]) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--help") {
            paxos::usage(std::cout);
            return 0;
        }
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            paxos::selfTest(std::cout);
            return 0;
        }
        if (argc == 3 && std::string(argv[1]) == "--scenario") {
            const std::string name = argv[2];
            for (const auto& scenario : paxos::kScenarios) {
                if (name == scenario) {
                    paxos::Simulation simulation(std::cout);
                    paxos::runScenario(name, simulation, std::cout);
                    return 0;
                }
            }
        }
        std::cerr << "Invalid arguments or unknown scenario.\n";
        paxos::usage(std::cerr);
        return 1;
    } catch (const std::exception& error) {
        std::cerr << "ERROR: " << error.what() << '\n';
        return 1;
    }
}
