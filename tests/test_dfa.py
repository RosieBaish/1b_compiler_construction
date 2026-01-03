from string import ascii_lowercase

from dfa import DFA
from cfg import Token


def test_empty_dfa():
    dfa = DFA({"0", "1"}, set(ascii_lowercase), lambda _q, _c: "0", "0", "1")
    assert not dfa.test_string("")
    assert not dfa.test_string("a")


def test_a():
    dfa = DFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: "1" if q == "0" and c == "a" else set(),
        "0",
        {"1"},
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert not dfa.test_string("aa")


def test_a_or_b():
    dfa = DFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: "1" if q == "0" and c in {"a", "b"} else set(),
        "0",
        {"1"},
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
            return "1"
        if q == "1" and c == "b":
            return "2"
        return set()

    dfa = DFA(
        {"0", "1", "2"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"2"},
    )

    assert dfa.test_string("ab")
    assert not dfa.test_string("ba")
    assert not dfa.test_string("ac")
    assert not dfa.test_string("a")
    assert not dfa.test_string("b")


def test_a_plus():
    def transition_function(q: str, c: str) -> set[str]:
        if q == "0" and c == "a":
            return "1"
        if q in {"1", "2"} and c == "a":
            return "2"
        return "Error"

    dfa = DFA(
        {"0", "1", "2", "Error"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"1", "2"},
    )

    assert not dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert dfa.test_string("aa")
    assert dfa.test_string("aaaaaaa")
    assert not dfa.test_string("aab")


def test_a_star():
    dfa = DFA(
        {"0", "1", "Error"},
        set(ascii_lowercase),
        lambda q, c: "1" if q in {"0", "1"} and c == "a" else "Error",
        "0",
        {"0", "1"},
    )

    assert dfa.test_string("")
    assert dfa.test_string("a")
    assert not dfa.test_string("b")
    assert dfa.test_string("aa")
    assert dfa.test_string("aaaaaaa")
    assert not dfa.test_string("aab")


def test_notes():
    """The test case from slide 19 of lecture 2, L((a or b)*abb).
    It's the DFA construction of the NFA on slide 9
    AKA any string containing only a and b that ends abb"""

    def transition_function(q: str, c: str) -> set[str]:
        delta: map[str, set[str]] = {}
        if q == "123458":
            delta = {
                "a": "2345789",
                "b": "235678",
            }
        elif q == "2345789":
            delta = {
                "a": "2345789",
                "b": "23567810",
            }
        elif q == "23567811":
            delta = {
                "a": "2345789",
                "b": "235678",
            }
        elif q == "235678":
            delta = {
                "a": "2345789",
                "b": "235678",
            }
        elif q == "23567810":
            delta = {
                "a": "2345789",
                "b": "23567811",
            }

        assert c in delta
        return delta[c]

    dfa = DFA(
        {
            "123458",
            "2345789",
            "23567811",
            "235678",
            "23567810",
        },
        {"a", "b"},
        transition_function,
        "123458",
        {"23567811"},
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


def test_typed_dfa():
    # This is test_a_star from above, but with a typed DFA

    a = Token("a")
    b = Token("b")

    dfa = DFA(
        {0, 1, -1},
        {a, b},
        lambda q, c: 1 if q in {0, 1} and c == a else -1,
        0,
        {0, 1},
    )

    assert dfa.test_string([])
    assert dfa.test_string([a])
    assert not dfa.test_string([b])
    assert dfa.test_string([a, a])
    assert dfa.test_string([a, a, a, a, a, a, a])
    assert not dfa.test_string([a, a, b])
