import pytest

from nfa import NFA
from regex import Regex, EmptyRegex


def test_empty_regex():
    nfa = NFA.from_regex(EmptyRegex(), {"a", "b", "c"})
    assert not nfa.test_string("")
    assert not nfa.test_string("a")


def test_empty_string():
    nfa = NFA.from_regex(Regex.parse(""), {"a", "b", "c"})

    assert nfa.test_string("")
    assert not nfa.test_string("a")


def test_a():
    nfa = NFA.from_regex(Regex.parse("a"), {"a", "b", "c"})

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert not nfa.test_string("b")
    assert not nfa.test_string("aa")


def test_a_or_b():
    nfa = NFA.from_regex(Regex.parse("(a+b)"), {"a", "b", "c"})

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert nfa.test_string("b")
    assert not nfa.test_string("aa")
    assert not nfa.test_string("ab")
    assert not nfa.test_string("ba")


def test_ab():
    nfa = NFA.from_regex(Regex.parse("ab"), {"a", "b", "c"})

    assert nfa.test_string("ab")
    assert not nfa.test_string("ba")
    assert not nfa.test_string("ac")
    assert not nfa.test_string("a")
    assert not nfa.test_string("b")


def test_a_star():
    nfa = NFA.from_regex(Regex.parse("(a)*"), {"a", "b", "c"})

    assert nfa.test_string("")
    assert nfa.test_string("a")
    assert not nfa.test_string("b")
    assert nfa.test_string("aa")
    assert nfa.test_string("aaaaaaa")
    assert not nfa.test_string("aab")


def test_notes():
    """The test case from slide 9 of lecture 2, L((a or b)*abb).
    AKA any string containing only a and b that ends abb"""

    nfa = NFA.from_regex(Regex.parse("((a+b))*abb"), {"a", "b", "c"})

    assert nfa.test_string("abb")
    assert nfa.test_string("aaabb")
    assert nfa.test_string("abbabb")
    assert nfa.test_string("bbaaabb")
    assert nfa.test_string("babb")
    assert not nfa.test_string("abba")
    assert not nfa.test_string("abbb")
    assert not nfa.test_string("ab")
    assert not nfa.test_string("bb")


def test_exception_on_abstract_base_class():
    with pytest.raises(AssertionError):
        _ = NFA.from_regex(Regex(), set())
