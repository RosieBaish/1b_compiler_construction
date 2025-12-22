from collections.abc import Callable
from string import ascii_lowercase

import matplotlib.pyplot as plt
import networkx as nx  # type: ignore

from regex import (
    Regex,
    EmptyRegex,
    EpsilonRegex,
    CharacterRegex,
    OrRegex,
    ConcatenationRegex,
    StarRegex,
)


class NFA:
    def __init__(
        self,
        Q: set[str],  # WLOG, just say states are strings
        Sigma: set[str],
        delta: Callable[[str, str], set[str]],
        q_0: str,
        F: set[str],
    ):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F

        # Check that q_0 and everything in F are valid states.
        assert self.q_0 in self.Q, (self.q_0, self.Q)
        for q in self.F:
            assert q in self.Q, (q, self.Q)

        # Check that everything in Sigma is a character not a string
        for c in self.Sigma:
            assert len(c) == 1, c

    def epsilon_close(self, states: set[str]) -> set[str]:
        closure: set[str] = states.copy()  # Everything can epsilon transition to itself
        work_list = list(states)
        while len(work_list):
            q = work_list[0]
            next_states = list(self.delta(q, ""))
            for q1 in next_states:
                if q1 not in closure:
                    closure.add(q1)
                    work_list.append(q1)
            work_list = work_list[1:]
        return closure

    def test_string(self, string: str) -> bool:
        current_states = self.epsilon_close(set(self.q_0))
        next_states: set[str]

        for c in string:
            assert c in self.Sigma, (c, self.Sigma)

            next_states = set()
            for q in current_states:
                next_states |= self.delta(q, c)
            next_states = self.epsilon_close(next_states)

            current_states = next_states

        # We've parsed the whole string, so check if we're in an accept state
        for q in current_states:
            if q in self.F:
                return True
        return False

    @staticmethod
    def from_regex(regex: Regex, Sigma: set[str]) -> "NFA":
        """Construct an NFA out of the given regex,
        which should be an instance of one of the regex subclasses.
        The constructed regex must have at least 1 accept state to allow recursive constructions."""
        if isinstance(regex, EmptyRegex):
            return NFA({"0", "1"}, Sigma, lambda _q, _c: set(), "0", {"1"})
        elif isinstance(regex, EpsilonRegex):
            return NFA(
                {"0", "1"}, Sigma, lambda _q, c: {"1"} if c == "" else set(), "0", {"1"}
            )
        elif isinstance(regex, CharacterRegex):
            return NFA(
                {"0", "1"},
                Sigma,
                lambda q, c: {"1"} if c == regex.character and q == "0" else set(),
                "0",
                {"1"},
            )
        elif isinstance(regex, OrRegex):
            nfa1 = NFA.from_regex(regex.r1, Sigma)
            nfa2 = NFA.from_regex(regex.r2, Sigma)
            assert len(nfa1.F) > 0
            assert len(nfa2.F) > 0
            Q = {"0", "1"}
            for state in nfa1.Q:
                Q.add(f"r1_{state}")
            for state in nfa2.Q:
                Q.add(f"r2_{state}")

            def transition_function(q: str, c: str) -> set[str]:
                if q == "0" and c == "":
                    return {f"r1_{nfa1.q_0}", f"r2_{nfa2.q_0}"}
                if q.startswith("r1_"):
                    q_prime = q[3:]
                    response_prime = nfa1.delta(q_prime, c)
                    response = {f"r1_{q}" for q in response_prime}
                    if q_prime in nfa1.F and c == "":
                        # Finishing states of r1 get epsilon'd to "1"
                        response |= {"1"}
                    return response
                if q.startswith("r2_"):
                    q_prime = q[3:]
                    response_prime = nfa2.delta(q_prime, c)
                    response = {f"r2_{q}" for q in response_prime}
                    if q_prime in nfa2.F and c == "":
                        # Finishing states of r2 get epsilon'd to "1"
                        response |= {"1"}
                    return response
                return set()

            return NFA(Q, Sigma, transition_function, "0", {"1"})
        elif isinstance(regex, ConcatenationRegex):
            # The construction here doesn't epsilon, but it's easier to just stick them in here
            # rather than try to manipulate the internal states.
            nfa1 = NFA.from_regex(regex.r1, Sigma)
            nfa2 = NFA.from_regex(regex.r2, Sigma)
            assert len(nfa1.F) > 0
            assert len(nfa2.F) > 0
            Q = {"0", "1"}
            for state in nfa1.Q:
                Q.add(f"r1_{state}")
            for state in nfa2.Q:
                Q.add(f"r2_{state}")

            def transition_function(q: str, c: str) -> set[str]:
                if q == "0" and c == "":
                    return {f"r1_{nfa1.q_0}"}
                if q.startswith("r1_"):
                    q_prime = q[3:]
                    response_prime = nfa1.delta(q_prime, c)
                    response = {f"r1_{q}" for q in response_prime}
                    if q_prime in nfa1.F and c == "":
                        # Finishing states of r1 get epsilon'd to the start of r2
                        response |= {f"r2_{nfa2.q_0}"}
                    return response
                if q.startswith("r2_"):
                    q_prime = q[3:]
                    response_prime = nfa2.delta(q_prime, c)
                    response = {f"r2_{q}" for q in response_prime}
                    if q_prime in nfa2.F and c == "":
                        # Finishing states of r2 get epsilon'd to "1"
                        response |= {"1"}
                    return response
                return set()

            return NFA(Q, Sigma, transition_function, "0", {"1"})
        elif isinstance(regex, StarRegex):
            nfa = NFA.from_regex(regex.r, Sigma)
            assert len(nfa.F) > 0
            Q = {"0", "1"}
            for state in nfa.Q:
                Q.add(f"r_{state}")

            def transition_function(q: str, c: str) -> set[str]:
                if q == "0" and c == "":
                    return {f"r_{nfa.q_0}", "1"}
                if q.startswith("r_"):
                    q_prime = q[2:]
                    response_prime = nfa.delta(q_prime, c)
                    response = {f"r_{q}" for q in response_prime}
                    if q_prime in nfa.F and c == "":
                        # Finishing states of r get epsilon'd to r's start and "1"
                        response |= {f"r_{nfa.q_0}", "1"}
                    return response
                return set()

            return NFA(Q, Sigma, transition_function, "0", {"1"})
        else:
            assert isinstance(regex, Regex), regex
            assert False, "Regex is an abstract base class"

    def get_transition_function_as_lookup(self) -> dict[str, dict[str, set[str]]]:
        delta_prime: dict[str, dict[str, set[str]]] = {}
        for q in self.Q:
            delta_prime[q] = {}
            for c in self.Sigma | {""}:
                delta_prime[q][c] = self.delta(q, c)
        return delta_prime

    @staticmethod
    def group_transition_row(
        transition_row: dict[str, set[str]],
    ) -> list[tuple[set[str], str, set[str]]]:
        """transition_row is one row of the transition function, i.e. all the outbound edges for
        a particular state.
        Group it so that it is something like a -> {"1"}, [b-z] -> set()
        Output is a list of (set of chars, stringified version of that set, set of states they go to)
        """

        def group_char_set(input_set: set[str]) -> str:
            assert len(input_set)
            for char in input_set:
                assert len(char) in {0, 1}, char
            # Work with ascii/unicode values not characters for simplicity
            ascii_vals = sorted([ord(c) if c != "" else -1 for c in input_set])

            def my_chr(c: int) -> str:
                """Identical to chr but uses -1 for epsilon"""
                if c == -1:
                    return "ε"
                else:
                    return chr(c)

            if len(ascii_vals) == 1:
                return my_chr(ascii_vals[0])
            groups: list[str] = []
            current_group: list[int] = [ascii_vals[0]]

            def add_current_group(current_group: list[int]) -> None:
                if len(current_group) < 3:
                    groups.extend([my_chr(c) for c in current_group])
                else:
                    groups.append(
                        f"{my_chr(current_group[0])}-{my_chr(current_group[-1])}"
                    )

            for c in ascii_vals[1:]:
                if c - current_group[-1] == 1:
                    # Still contiguous
                    current_group.append(c)
                else:
                    add_current_group(current_group)
                    current_group = [c]
            add_current_group(current_group)

            return ",".join(groups)

        grouped_rows: dict[frozenset[str], set[str]] = {}
        # Dict from (output set) -> {set of chars that go to that output set}
        # I.e. reversed from transition_row
        unfrozen_sets: dict[frozenset[str], set[str]] = {}
        # Mapping from frozensets back to the originals
        for c, next_set in transition_row.items():
            frozen_next_set = frozenset(next_set)
            if frozen_next_set in grouped_rows:
                grouped_rows[frozen_next_set] |= {c}
            else:
                grouped_rows[frozen_next_set] = {c}
                unfrozen_sets[frozen_next_set] = next_set

        output: list[tuple[set[str], str, set[str]]] = []
        for frozen_next_set, chars in grouped_rows.items():
            assert isinstance(frozen_next_set, frozenset)
            next_set = unfrozen_sets[frozen_next_set]
            output.append((chars, group_char_set(chars), next_set))
        return output

    def plot(self) -> None:  # pragma: no cover
        G = nx.DiGraph()

        Q_list = sorted(list(self.Q))
        G.add_nodes_from(Q_list)

        edges: list[tuple[str, str]] = []
        edge_labels: dict[tuple[str, str], str] = {}

        delta_prime = self.get_transition_function_as_lookup()

        for q, transition_row in delta_prime.items():
            grouped_transition_row = NFA.group_transition_row(transition_row)
            for _, char_string, states in grouped_transition_row:
                for state in states:
                    edges.append((q, state))
                    edge_labels[(q, state)] = char_string

        G.add_edges_from(edges)

        pos = nx.spring_layout(G)

        nx.draw_networkx(
            G,
            pos=pos,
            node_color=["pink" if q in self.F else "blue" for q in Q_list],
            edge_color="black",
            connectionstyle="arc3,rad=0.2",
        )

        nx.draw_networkx_edge_labels(
            G,
            pos=pos,
            edge_labels=edge_labels,
            connectionstyle="arc3,rad=0.2",
        )

        plt.show()


def main() -> None:
    def test_and_print(nfa: NFA, string: str) -> None:
        print(string, "Accept" if nfa.test_string(string) else "Reject")

    def transition_function(q: str, c: str) -> set[str]:
        if q == "0" and c == "a":
            return {"1"}
        if q == "1" and c == "b":
            return {"2"}
        if q == "2" and c == "c":
            return {"3"}
        return set()

    nfa = NFA(
        {"0", "1", "2", "3"},
        set(ascii_lowercase[:6]),
        transition_function,
        "0",
        {"3"},
    )

    test_and_print(nfa, "abc")
    test_and_print(nfa, "def")
    test_and_print(nfa, "abd")
    test_and_print(nfa, "aaa")

    nfa.plot()
