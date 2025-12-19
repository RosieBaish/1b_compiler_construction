from string import ascii_lowercase

from nfa import NFA


def test_empty_regex():
    nfa = NFA({"0", "1"}, set(ascii_lowercase), lambda _q, _c: set(), "0", {"1"})
    assert not nfa.test_string("")
    assert not nfa.test_string("a")


def test_empty_string():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q in {"0", "1"} and c == "" else set(),
        "0",
        {"1"},
    )

    assert nfa.test_string("")
    assert not nfa.test_string("a")


def test_a():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q == "0" and c == "a" else set(),
        "0",
        {"1"},
    )

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert not nfa.test_string("b")
    assert not nfa.test_string("aa")


def test_a_or_b():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q == "0" and c in {"a", "b"} else set(),
        "0",
        {"1"},
    )

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert nfa.test_string("b")
    assert not nfa.test_string("aa")
    assert not nfa.test_string("ab")
    assert not nfa.test_string("ba")


def test_ab():
    def transition_function(q: str, c: str) -> set[str]:
        if q == "0" and c == "a":
            return {"1"}
        if q == "1" and c == "b":
            return {"2"}
        return set()

    nfa = NFA(
        {"0", "1", "2"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"2"},
    )

    assert nfa.test_string("ab")
    assert not nfa.test_string("ba")
    assert not nfa.test_string("ac")
    assert not nfa.test_string("a")
    assert not nfa.test_string("b")


def test_a_star():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q in {"0", "1"} and c == "a" else set(),
        "0",
        {"1"},
    )

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert not nfa.test_string("b")
    assert nfa.test_string("aa")
    assert nfa.test_string("aaaaaaa")
    assert not nfa.test_string("aab")


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

    nfa = NFA(
        set(str(i) for i in range(5)),
        set(ascii_lowercase),
        transition_function,
        "1",
        {"4"},
    )

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert not nfa.test_string("b")
    assert not nfa.test_string("aa")


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

    nfa = NFA(
        set(str(i) for i in range(1, 12)),
        set(ascii_lowercase),
        transition_function,
        "1",
        {"11"},
    )

    assert nfa.test_string("abb")
    assert nfa.test_string("aaabb")
    assert nfa.test_string("abbabb")
    assert nfa.test_string("bbaaabb")
    assert nfa.test_string("babb")
    assert not nfa.test_string("abba")
    assert not nfa.test_string("abbb")
    assert not nfa.test_string("ab")
    assert not nfa.test_string("bb")
