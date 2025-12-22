from string import ascii_lowercase

from nfa import NFA


def test_empty_nfa():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda _q, _c: set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "1"},
        state_rankings=["0", "1"],
    )
    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None


def test_empty_string():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q in {"0", "1"} and c == "" else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "1"},
        state_rankings=["0", "1"],
    )

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "1"

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "1"


def test_a():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q == "0" and c == "a" else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "1"},
        state_rankings=["0", "1"],
    )

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "1"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "1"


def test_a_or_b():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q == "0" and c in {"a", "b"} else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "a+b"},
        state_rankings=["0", "1"],
    )

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+b"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+b"

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+b"

    nfa.test_string("ab")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+b"

    nfa.test_string("ba")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+b"


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
        tags={"0": "0", "1": "1", "2": "ab"},
        state_rankings=["0", "1", "2"],
    )

    nfa.test_string("ab")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_state == "2"
    assert nfa.last_accept_tag == "ab"

    nfa.test_string("ba")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("ac")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None


def test_a_plus():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q in {"0", "1"} and c == "a" else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "a+"},
        state_rankings=["0", "1"],
    )

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+"

    nfa.test_string("aaaaaaa")
    assert nfa.num_chars_accepted == 7
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+"

    nfa.test_string("aab")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a+"


def test_a_star():
    nfa = NFA(
        {"0", "1"},
        set(ascii_lowercase),
        lambda q, c: {"1"} if q in {"0", "1"} and c in {"a", ""} else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "a*"},
        state_rankings=["0", "1"],
    )

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"

    nfa.test_string("aaaaaaa")
    assert nfa.num_chars_accepted == 7
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"

    nfa.test_string("aab")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_state == "1"
    assert nfa.last_accept_tag == "a*"


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

    nfa = NFA(
        set(state_list),
        set(ascii_lowercase),
        transition_function,
        "1",
        {"11"},
        tags={str(i): str(i) for i in state_list},
        state_rankings=state_list,
    )

    nfa.test_string("abb")
    assert nfa.num_chars_accepted == 3
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("aaabb")
    assert nfa.num_chars_accepted == 5
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("abbabb")
    assert nfa.num_chars_accepted == 6
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("bbaaabb")
    assert nfa.num_chars_accepted == 7
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("babb")
    assert nfa.num_chars_accepted == 4
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("abba")
    assert nfa.num_chars_accepted == 3
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("abbb")
    assert nfa.num_chars_accepted == 3
    assert nfa.last_accept_state == "11"
    assert nfa.last_accept_tag == "11"

    nfa.test_string("ab")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None

    nfa.test_string("bb")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_state is None
    assert nfa.last_accept_tag is None
