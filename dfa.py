from collections.abc import Callable
from string import ascii_lowercase

from nfa import NFA


class DFA:
    def __init__(
        self,
        Q: set[str],  # WLOG, just say states are strings
        Sigma: set[str],
        delta: Callable[[str, str], str],
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

    def __repr__(self) -> str:
        return f"DFA <{self.Q}, {self.Sigma}, delta, '{self.q_0}', {self.F}>"

    def test_string(self, string: str) -> bool:
        q = self.q_0

        for c in string:
            assert c in self.Sigma, (c, self.Sigma)
            q = self.delta(q, c)

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
            assert s[0] == "{", s
            assert s[-1] == "}", s
            return set(s[1:-1].split(","))

        def powerset_str(s: set[str]) -> set[str]:
            num_bits = len(s)
            ps: set[str] = set()
            elements = sorted(list(s))
            for i in range(2**num_bits):
                set_i: set[str] = set()
                for j in range(len(elements)):
                    if (2**j) & i:
                        set_i.add(elements[j])
                ps.add(set_to_string(set_i))
            return ps

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

        Q_prime = powerset_str(nfa.Q)

        def delta_prime(S: str, a: str) -> str:
            output_set = set()
            for q in string_to_set(S):
                output_set |= nfa.delta(q, a)
            return set_to_string(epsilon_closure(output_set, nfa.delta))

        print(nfa.q_0)
        print(epsilon_closure({nfa.q_0}, nfa.delta))
        q_0_prime = set_to_string(epsilon_closure({nfa.q_0}, nfa.delta))
        print(q_0_prime)

        F_prime: set[str] = set()
        for S in Q_prime:
            if not string_to_set(S).isdisjoint(nfa.F):
                F_prime.add(S)

        return DFA(Q_prime, nfa.Sigma, delta_prime, q_0_prime, F_prime)


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
