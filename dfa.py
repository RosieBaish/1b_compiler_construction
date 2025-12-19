from collections.abc import Callable
from string import ascii_lowercase


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

    def test_string(self, string: str) -> bool:
        q = self.q_0

        for c in string:
            assert c in self.Sigma, (c, self.Sigma)
            q = self.delta(q, c)

        # We've parsed the whole string, so check if we're in an accept state
        return q in self.F


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
