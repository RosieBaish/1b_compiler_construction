from regex import Regex, EmptyRegex


def test_empty_regex():
    regex = EmptyRegex()
    assert not regex.test_string("")
    assert not regex.test_string("a")


def test_empty_string():
    regex = Regex.parse("")

    assert regex.test_string("")
    assert not regex.test_string("a")


def test_a():
    regex = Regex.parse("a")

    assert not regex.test_string("")
    assert regex.test_string("a")
    assert not regex.test_string("b")
    assert not regex.test_string("aa")


def test_range_a():
    regex = Regex.parse("[a]")

    assert not regex.test_string("")
    assert regex.test_string("a")
    assert not regex.test_string("b")
    assert not regex.test_string("d")
    assert not regex.test_string("aa")


def test_range_ab():
    regex = Regex.parse("[ab]")

    assert not regex.test_string("")
    assert regex.test_string("a")
    assert regex.test_string("b")
    assert not regex.test_string("d")
    assert not regex.test_string("aa")


def test_range_abc():
    regex = Regex.parse("[a-c]")

    assert not regex.test_string("")
    assert regex.test_string("a")
    assert regex.test_string("b")
    assert regex.test_string("c")
    assert not regex.test_string("d")
    assert not regex.test_string("aa")


def test_a_or_b():
    regex = Regex.parse("(a+b)")

    assert not regex.test_string("")
    assert regex.test_string("a")
    assert regex.test_string("b")
    assert not regex.test_string("aa")
    assert not regex.test_string("ab")
    assert not regex.test_string("ba")


def test_ab():
    regex = Regex.parse("ab")

    assert regex.test_string("ab")
    assert not regex.test_string("ba")
    assert not regex.test_string("ac")
    assert not regex.test_string("a")
    assert not regex.test_string("b")


def test_a_star():
    regex = Regex.parse("(a)*")

    assert regex.test_string("")
    assert regex.test_string("a")
    assert not regex.test_string("b")
    assert regex.test_string("aa")
    assert regex.test_string("aaaaaaa")
    assert not regex.test_string("aab")


def test_notes():
    """The test case from slide 9 of lecture 2, L((a or b)*abb).
    AKA any string containing only a and b that ends abb"""

    regex = Regex.parse("((a+b))*abb")

    assert regex.test_string("abb")
    assert regex.test_string("aaabb")
    assert regex.test_string("abbabb")
    assert regex.test_string("bbaaabb")
    assert regex.test_string("babb")
    assert not regex.test_string("abba")
    assert not regex.test_string("abbb")
    assert not regex.test_string("ab")
    assert not regex.test_string("bb")
