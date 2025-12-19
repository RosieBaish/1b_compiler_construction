from collections.abc import Callable
from string import ascii_lowercase


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
        return {"Error"}

    nfa = NFA(
        {"0", "1", "2", "3", "Error"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"3"},
    )

    test_and_print(nfa, "abc")
    test_and_print(nfa, "def")
    test_and_print(nfa, "abd")
    test_and_print(nfa, "aaa")
