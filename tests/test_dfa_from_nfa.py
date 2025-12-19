from dfa import DFA
from nfa import NFA


def test_empty_nfa():
    dfa = DFA.fromNFA(NFA({"0", "1"}, {"a", "b"}, lambda _q, _c: set(), "0", {"1"}))
    assert not dfa.test_string("")
    assert not dfa.test_string("a")


def test_empty_string():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            {"a", "b"},
            lambda q, c: {"1"} if q in {"0", "1"} and c == "" else set(),
            "0",
            {"1"},
        )
    )

    assert dfa.test_string("")
    assert not dfa.test_string("a")


def test_a():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            {"a", "b"},
            lambda q, c: {"1"} if q == "0" and c == "a" else set(),
            "0",
            {"1"},
        )
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert not dfa.test_string("aa")


def test_a_or_b():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            {"a", "b"},
            lambda q, c: {"1"} if q == "0" and c in {"a", "b"} else set(),
            "0",
            {"1"},
        )
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert dfa.test_string("b")
    assert not dfa.test_string("aa")
    assert not dfa.test_string("ab")
    assert not dfa.test_string("ba")


def test_ab():
    def transition_function(q: str, c: str) -> set[str]:
        if q == "0" and c == "a":
            return {"1"}
        if q == "1" and c == "b":
            return {"2"}
        return set()

    dfa = DFA.fromNFA(
        NFA(
            {"0", "1", "2"},
            {"a", "b", "c"},
            transition_function,
            "0",
            {"2"},
        )
    )

    assert dfa.test_string("ab")
    assert not dfa.test_string("ba")
    assert not dfa.test_string("ac")
    assert not dfa.test_string("a")
    assert not dfa.test_string("b")


def test_a_plus():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            {"a", "b"},
            lambda q, c: {"1"} if q in {"0", "1"} and c == "a" else set(),
            "0",
            {"1"},
        )
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert dfa.test_string("aa")
    assert dfa.test_string("aaaaaaa")
    assert not dfa.test_string("aab")


def test_a_star():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            {"a", "b"},
            lambda q, c: {"1"} if q in {"0", "1"} and c in {"a", ""} else set(),
            "0",
            {"1"},
        )
    )

    assert dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert dfa.test_string("aa")
    assert dfa.test_string("aaaaaaa")
    assert not dfa.test_string("aab")


def test_epsilon_closure_recursive():
    """Check that the epsilon closure is being done recursively, should accept only 'a'"""

    def transition_function(q: str, c: str) -> set[str]:
        if q == "0":
            delta = {
                "": {"1"},
            }
        elif q == "1":
            delta = {
                "": {"2"},
            }
        elif q == "2":
            delta = {
                "": {"3"},
            }
        elif q == "3":
            delta = {
                "a": {"4"},
            }
        elif q == "4":
            delta = {}

        if c in delta:
            return delta[c]
        else:
            return set()

    dfa = DFA.fromNFA(
        NFA(
            set(str(i) for i in range(5)),
            {"a", "b"},
            transition_function,
            "1",
            {"4"},
        )
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert not dfa.test_string("aa")


def test_notes():
    """The test case from slide 9 of lecture 2, L((a or b)*abb).
    AKA any string containing only a and b that ends abb"""

    def transition_function(q: str, c: str) -> set[str]:
        delta: map[str, set[str]] = {}
        if q == "1":
            delta = {
                "": {"2", "8"},
            }
        elif q == "2":
            delta = {
                "": {"3", "5"},
            }
        elif q == "3":
            delta = {
                "a": {"4"},
            }
        elif q == "4":
            delta = {
                "": {"7"},
            }
        elif q == "5":
            delta = {
                "b": {"6"},
            }
        elif q == "6":
            delta = {
                "": {"7"},
            }
        elif q == "7":
            delta = {
                "": {"2", "8"},
            }
        elif q == "8":
            delta = {
                "a": {"9"},
            }
        elif q == "9":
            delta = {
                "b": {"10"},
            }
        elif q == "10":
            delta = {
                "b": {"11"},
            }
        elif q == "11":
            delta = {}

        if c in delta:
            return delta[c]
        else:
            return set()

    dfa = DFA.fromNFA(
        NFA(
            set(str(i) for i in range(1, 12)),
            {"a", "b"},
            transition_function,
            "1",
            {"11"},
        )
    )

    assert dfa.test_string("abb")
    assert dfa.test_string("aaabb")
    assert dfa.test_string("abbabb")
    assert dfa.test_string("bbaaabb")
    assert dfa.test_string("babb")
    assert not dfa.test_string("abba")
    assert not dfa.test_string("abbb")
    assert not dfa.test_string("ab")
    assert not dfa.test_string("bb")
