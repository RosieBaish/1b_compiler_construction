from string import ascii_lowercase

from dfa import DFA
from nfa import NFA


def test_empty_nfa():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda _q, _c: set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "1"},
            state_rankings=["0", "1"],
        )
    )
    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None


def test_empty_string():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda q, c: {"1"} if q in {"0", "1"} and c == "" else set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "1"},
            state_rankings=["0", "1"],
        )
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "1"

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "1"


def test_a():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda q, c: {"1"} if q == "0" and c == "a" else set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "1"},
            state_rankings=["0", "1"],
        )
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "1"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "1"


def test_a_or_b():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda q, c: {"1"} if q == "0" and c in {"a", "b"} else set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "a+b"},
            state_rankings=["0", "1"],
        )
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+b"


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
            set(ascii_lowercase),
            transition_function,
            "0",
            {"2"},
            tags={"0": "0", "1": "1", "2": "ab"},
            state_rankings=["0", "1", "2"],
        )
    )

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "ab"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("ac")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None


def test_a_plus():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda q, c: {"1"} if q in {"0", "1"} and c == "a" else set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "a+"},
            state_rankings=["0", "1"],
        )
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "a+"


def test_a_star():
    dfa = DFA.fromNFA(
        NFA(
            {"0", "1"},
            set(ascii_lowercase),
            lambda q, c: {"1"} if q in {"0", "1"} and c in {"a", ""} else set(),
            "0",
            {"1"},
            tags={"0": "0", "1": "a*"},
            state_rankings=["0", "1"],
        )
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "a*"


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

    state_list = [str(i) for i in range(1, 12)]

    dfa = DFA.fromNFA(
        NFA(
            set(state_list),
            set(ascii_lowercase),
            transition_function,
            "1",
            {"11"},
            tags={str(i): str(i) for i in state_list},
            state_rankings=state_list,
        )
    )

    dfa.test_string("abb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "11"

    dfa.test_string("aaabb")
    assert dfa.num_chars_accepted == 5
    assert dfa.last_accept_tag == "11"

    dfa.test_string("abbabb")
    assert dfa.num_chars_accepted == 6
    assert dfa.last_accept_tag == "11"

    dfa.test_string("bbaaabb")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "11"

    dfa.test_string("babb")
    assert dfa.num_chars_accepted == 4
    assert dfa.last_accept_tag == "11"

    dfa.test_string("abba")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "11"

    dfa.test_string("abbb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "11"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("bb")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None
