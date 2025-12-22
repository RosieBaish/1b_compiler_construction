from collections.abc import Callable
from string import ascii_lowercase

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
