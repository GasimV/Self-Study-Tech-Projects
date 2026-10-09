// Classical oral-message agreement OM(m), NOT PBFT or a replicated log.
// Known senders, reliable delivery of sent messages, detectable omissions.
// Transport models faulty senders; the agreement procedure knows no fault list.
#include <algorithm>
#include <functional>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <vector>

namespace bft_dsa {
enum class Order { RETREAT, ATTACK };
using Path = std::vector<int>;
using Transport = std::function<std::optional<Order>(int, int, Order, const Path&)>;

const char* Name(Order order) {
    return order == Order::ATTACK ? "ATTACK" : "RETREAT";
}

Order Receive(int sender, int receiver, Order order, const Path& path,
              const Transport& send) {
    return send(sender, receiver, order, path).value_or(Order::RETREAT);
}

Order Majority(const std::vector<Order>& reports) {
    const auto attacks = static_cast<std::size_t>(
        std::count(reports.begin(), reports.end(), Order::ATTACK));
    return attacks > reports.size() / 2 ? Order::ATTACK : Order::RETREAT;
}

// group[0] is this call's commander. Results follow group[1..].
std::vector<Order> Relay(int depth, const std::vector<int>& group, Order order,
                         const Transport& send, Path& path) {
    path.push_back(group[0]);
    const std::size_t k = group.size() - 1;
    std::vector<Order> received(k);
    for (std::size_t i = 0; i < k; ++i) {
        received[i] = Receive(group[0], group[i + 1], order, path, send);
    }
    if (depth == 0) {
        path.pop_back();
        return received; // OM(0): use the direct order, including the default.
    }

    // Row = recipient; column = lieutenant whose report is being combined.
    std::vector<std::vector<Order>> reports(k, std::vector<Order>(k));
    for (std::size_t i = 0; i < k; ++i) {
        reports[i][i] = received[i]; // Each recipient includes its own direct order.
        std::vector<int> child{group[i + 1]};
        for (std::size_t j = 0; j < k; ++j) {
            if (j != i) child.push_back(group[j + 1]);
        }
        const auto relayed = Relay(depth - 1, child, received[i], send, path);
        std::size_t next = 0;
        for (std::size_t j = 0; j < k; ++j) {
            if (j != i) reports[j][i] = relayed[next++];
        }
    }
    for (std::size_t i = 0; i < k; ++i) received[i] = Majority(reports[i]);
    path.pop_back();
    return received;
}

// Fixed membership is IDs 0..n-1: identities are distinct by construction.
// The commander has no returned decision; only lieutenant decisions are defined.
// Guarantee: n >= 3m+1 and at most m faulty participants, under stated assumptions.
std::vector<std::optional<Order>> OralMessages(int n, int m, int commander,
                                              Order order, const Transport& send) {
    if (n < 2 || m < 0 || m > n - 2 || commander < 0 || commander >= n || !send ||
        (order != Order::ATTACK && order != Order::RETREAT)) {
        throw std::invalid_argument("Invalid membership, depth, commander, order, or transport");
    }
    // Do NOT require n >= 3m+1 here: outside-bound experiments remain executable.
    std::vector<int> group{commander};
    for (int id = 0; id < n; ++id) if (id != commander) group.push_back(id);
    Path path;
    const auto decisions = Relay(m, group, order, send, path);
    std::vector<std::optional<Order>> result(static_cast<std::size_t>(n));
    for (std::size_t i = 1; i < group.size(); ++i) result[group[i]] = decisions[i - 1];
    return result;
}
} // namespace bft_dsa

// A simulator can identify injected faults; real recipients cannot consult this list.
void Demonstrate(const char* title, const std::vector<int>& faulty,
                 const bft_dsa::Transport& behavior) {
    using namespace bft_dsa;
    std::cout << "SCENARIO: " << title << "\nN=4, OM(1), configured fault budget=1\nFAULTY:";
    if (faulty.empty()) std::cout << " none";
    for (int id : faulty) std::cout << ' ' << static_cast<char>('A' + id);
    std::cout << "\nGUARANTEE: " << (faulty.size() <= 1 ? "within configured fault bound"
                                                          : "outside the fault guarantee") << '\n';
    const auto traced = [&](int sender, int receiver, Order order, const Path& path) {
        const auto delivered = behavior(sender, receiver, order, path);
        std::cout << "  " << (path.size() == 1 ? "DIRECT " : "RELAY  ");
        for (int id : path) std::cout << static_cast<char>('A' + id) << " -> ";
        std::cout << static_cast<char>('A' + receiver) << ": "
                  << (delivered ? Name(*delivered) : "MISSING (default RETREAT)") << '\n';
        return delivered;
    };
    const auto decisions = OralMessages(4, 1, 0, Order::ATTACK, traced);
    std::optional<Order> first;
    bool agree = true;
    std::cout << "LOYAL LIEUTENANT DECISIONS:\n";
    for (int id = 1; id < 4; ++id) {
        if (std::find(faulty.begin(), faulty.end(), id) != faulty.end()) continue;
        std::cout << "  " << static_cast<char>('A' + id) << " = " << Name(*decisions[id]) << '\n';
        if (first && decisions[id] != first) agree = false;
        if (!first) first = decisions[id];
    }
    std::cout << "RESULT: loyal lieutenants " << (agree ? "agree on " : "disagree")
              << (agree ? Name(*first) : "") << "\n\n";
}

int main(int argc, char**) {
    if (argc != 1) {
        std::cerr << "Usage: bft_dsa.exe\n";
        return 1;
    }
    using namespace bft_dsa;
    Demonstrate("all loyal", {}, [](int, int, Order order, const Path&) {
        return order;
    });
    Demonstrate("dishonest lieutenant D", {3}, [](int sender, int receiver, Order order, const Path&) {
        return sender == 3 && receiver == 1 ? Order::RETREAT : order;
    });
    Demonstrate("dishonest commander A", {0}, [](int sender, int receiver, Order order, const Path&) {
        return sender == 0 && receiver == 2 ? Order::RETREAT : order;
    });
    Demonstrate("two traitors A and D", {0, 3}, [](int sender, int receiver, Order order, const Path&) {
        if (sender == 0 || sender == 3) return receiver == 1 ? Order::ATTACK : Order::RETREAT;
        return order;
    });
    return 0;
}
