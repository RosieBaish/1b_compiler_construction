from string import ascii_lowercase

from dfa import DFA


def test_empty_dfa():
    dfa = DFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda _q, _c: "0",
        "0",
        "1",
        tags={"0": "0", "1": "1"},
    )
    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None


def test_a():
    dfa = DFA(
        {"0", "1", "Error"},
        set(ascii_lowercase),
        lambda q, c: "1" if q == "0" and c == "a" else "Error",
        "0",
        {"1"},
        tags={"0": "0", "1": "1", "Error": "Error"},
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "1"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "1"


def test_a_or_b():
    dfa = DFA(
        {"0", "1", "Error"},
        set(ascii_lowercase),
        lambda q, c: "1" if q == "0" and c in {"a", "b"} else "Error",
        "0",
        {"1"},
        tags={"0": "0", "1": "a+b", "Error": "Error"},
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+b"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+b"


def test_ab():
    def transition_function(q: str, c: str) -> set[str]:
        if q == "0" and c == "a":
            return "1"
        if q == "1" and c == "b":
            return "2"
        return "Error"

    dfa = DFA(
        {"0", "1", "2", "Error"},
        set(ascii_lowercase),
        transition_function,
        "0",
        {"2"},
        tags={"0": "0", "1": "1", "2": "ab", "Error": "Error"},
    )

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_state == "2"
    assert dfa.last_accept_tag == "ab"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("ac")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None


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
        tags={"0": "0", "1": "a+", "2": "a+", "Error": "Error"},
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_state == "2"
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_state == "2"
    assert dfa.last_accept_tag == "a+"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_state == "2"
    assert dfa.last_accept_tag == "a+"


def test_a_star():
    dfa = DFA(
        {"0", "1", "Error"},
        set(ascii_lowercase),
        lambda q, c: "1" if q in {"0", "1"} and c == "a" else "Error",
        "0",
        {"0", "1"},
        tags={"0": "a*", "1": "a*", "Error": "Error"},
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state == "0"
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state == "0"
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a*"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_state == "1"
    assert dfa.last_accept_tag == "a*"


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

        c in delta
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
        tags={
            "123458": "State 1",
            "2345789": "State 2",
            "23567811": "State 3",
            "235678": "State 4",
            "23567810": "State 5",
        },
    )

    dfa.test_string("abb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("aaabb")
    assert dfa.num_chars_accepted == 5
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("abbabb")
    assert dfa.num_chars_accepted == 6
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("bbaaabb")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("babb")
    assert dfa.num_chars_accepted == 4
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("abba")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("abbb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_state == "23567811"
    assert dfa.last_accept_tag == "State 3"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None

    dfa.test_string("bb")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_state is None
    assert dfa.last_accept_tag is None
