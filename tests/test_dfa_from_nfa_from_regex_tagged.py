from dfa import DFA
from nfa import NFA
from regex import EmptyRegex, Regex


def test_empty_nfa():
    dfa = DFA.fromNFA(NFA.from_regex(EmptyRegex(), {"a", "b"}, accept_tag="Accept"))

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None


def test_empty_string():
    dfa = DFA.fromNFA(NFA.from_regex(Regex.parse(""), {"a", "b"}, accept_tag="Accept"))

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "Accept"


def test_a():
    dfa = DFA.fromNFA(NFA.from_regex(Regex.parse("a"), {"a", "b"}, accept_tag="Accept"))

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"


def test_range_a():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("[a]"), {"a", "b", "c", "d"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"


def test_range_ab():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("[ab]"), {"a", "b", "c", "d"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("d")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"


def test_range_abc():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("[a-c]"), {"a", "b", "c", "d"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("c")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("d")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"


def test_a_or_b():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("(a+b)"), {"a", "b"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ba")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"


def test_ab():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("ab"), {"a", "b", "c"}, accept_tag="Accept")
    )

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "Accept"

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
        NFA.from_regex(Regex.parse("a(a)*"), {"a", "b"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "Accept"


def test_a_star():
    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("(a)*"), {"a", "b"}, accept_tag="Accept")
    )

    dfa.test_string("")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("a")
    assert dfa.num_chars_accepted == 1
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("b")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aa")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aaaaaaa")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aab")
    assert dfa.num_chars_accepted == 2
    assert dfa.last_accept_tag == "Accept"


def test_notes():
    """The test case from slide 9 of lecture 2, L((a or b)*abb).
    AKA any string containing only a and b that ends abb"""

    dfa = DFA.fromNFA(
        NFA.from_regex(Regex.parse("((a+b))*abb"), {"a", "b"}, accept_tag="Accept")
    )

    dfa.test_string("abb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("aaabb")
    assert dfa.num_chars_accepted == 5
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("abbabb")
    assert dfa.num_chars_accepted == 6
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("bbaaabb")
    assert dfa.num_chars_accepted == 7
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("babb")
    assert dfa.num_chars_accepted == 4
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("abba")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("abbb")
    assert dfa.num_chars_accepted == 3
    assert dfa.last_accept_tag == "Accept"

    dfa.test_string("ab")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None

    dfa.test_string("bb")
    assert dfa.num_chars_accepted == 0
    assert dfa.last_accept_tag is None
