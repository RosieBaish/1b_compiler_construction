from collections.abc import Callable
from string import ascii_lowercase
from typing import Optional

from nfa import NFA


class DFA:
    def __init__(
        self,
        Q: set[str],  # WLOG, just say states are strings
        Sigma: set[str],
        delta: Callable[[str, str], str],
        q_0: str,
        F: set[str],
        tags: dict[str, str] = {},  # Optional mapping from states to tags
    ):
        self.Q = Q
        self.Sigma = Sigma
        self.delta = delta
        self.q_0 = q_0
        self.F = F
        self.tags = tags

        # Check that q_0 and everything in F are valid states.
        assert self.q_0 in self.Q, (self.q_0, self.Q)
        for q in self.F:
            assert q in self.Q, (q, self.Q)

        # Check that everything in Sigma is a character not a string
        for c in self.Sigma:
            assert len(c) == 1, c

        # Tags is either empty, or contains every state as a key
        if len(self.tags) > 0:
            assert len(self.Q) == len(self.tags)
            for q in self.Q:
                assert q in self.tags

        self.num_chars_accepted = 0
        self.last_accept_state: Optional[str] = None
        self.last_accept_tag: Optional[str] = None

    def __repr__(self) -> str:
        return f"DFA <{self.Q}, {self.Sigma}, delta, '{self.q_0}', {self.F}>"

    def test_string(self, string: str) -> bool:
        q = self.q_0
        num_chars_consumed = 0  # Running total
        self.num_chars_accepted = 0  # Number of chars accepted
        self.last_accept_state = q if q in self.F else None
        self.last_accept_tag = self.tags[q] if len(self.tags) and q in self.F else None

        for c in string:
            assert c in self.Sigma, (c, self.Sigma)
            q = self.delta(q, c)

            num_chars_consumed += 1
            if q in self.F:
                self.num_chars_accepted = num_chars_consumed
                self.last_accept_state = q
                if len(self.tags):
                    self.last_accept_tag = self.tags[q]

        # We've parsed the whole string, so check if we're in an accept state
        return q in self.F

    @staticmethod
    def fromNFA(nfa: NFA) -> "DFA":
        def set_to_string(s: set[str]) -> str:
            try:
                elements = sorted(list(s), key=int)
            except Exception:
                elements = sorted(list(s))
            return "{" + ",".join(elements) + "}"

        def string_to_set(s: str) -> set[str]:
            if s == "{}":
                # This was otherwise returning the set containing the empty string which is wrong
                return set()
            assert s[0] == "{", s
            assert s[-1] == "}", s
            return set(s[1:-1].split(","))

        def epsilon_closure(
            s: set[str], delta: Callable[[str, str], set[str]]
        ) -> set[str]:
            """Algorithm from the notes"""
            stack = list(s)
            result = s.copy()
            while len(stack):
                q, stack = stack[0], stack[1:]
                for u in delta(q, ""):
                    if u not in result:
                        result.add(u)
                        stack.append(u)
            return result

        def delta_prime(S: str, a: str) -> str:
            output_set = set()
            for q in string_to_set(S):
                output_set |= nfa.delta(q, a)
            return set_to_string(epsilon_closure(output_set, nfa.delta))

        q_0_prime = set_to_string(epsilon_closure({nfa.q_0}, nfa.delta))

        # It's weird to compute the states after we've got the transition function
        # and start state, but because states are just strings it works.
        # We're just computing the reachable sets here, rather than the full powerset
        Q_prime = {q_0_prime}
        work_list = [q_0_prime]
        while len(work_list):
            q = work_list[0]
            for c in nfa.Sigma:
                output = delta_prime(q, c)
                if output not in Q_prime:
                    Q_prime.add(output)
                    if output not in work_list:
                        work_list.append(output)
            work_list = work_list[1:]

        F_prime: set[str] = set()
        for S in Q_prime:
            if not string_to_set(S).isdisjoint(nfa.F):
                F_prime.add(S)

        tags_prime: dict[str, str] = {}
        if len(nfa.tags):
            for S in Q_prime:
                S_list = sorted(
                    [s for s in list(string_to_set(S)) if s in nfa.F],
                    key=lambda x: nfa.state_rankings.index(x),
                )
                if S_list == []:
                    tags_prime[S] = "set()"
                else:
                    tags_prime[S] = nfa.tags[S_list[0]]

        return DFA(Q_prime, nfa.Sigma, delta_prime, q_0_prime, F_prime, tags_prime)


def main() -> None:
    def test_and_print(dfa: DFA, string: str) -> None:
        print(string, "Accept" if dfa.test_string(string) else "Reject")

    def transition_function(q: str, c: str) -> str:
        if q == "0" and c == "a":
            return "1"
        if q == "1" and c == "b":
            return "2"
        if q == "2" and c == "c":
            return "3"
        return "Error"

    dfa = DFA(
        {"0", "1", "2", "3", "Error"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"3"},
    )

    test_and_print(dfa, "abc")
    test_and_print(dfa, "def")
    test_and_print(dfa, "abd")
    test_and_print(dfa, "aaa")
