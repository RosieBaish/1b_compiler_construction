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


def test_literal_backslash_alone():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse(single_backslash + single_backslash)

    assert regex.test_string(single_backslash)
    assert not regex.test_string(single_backslash + single_backslash)


def test_literal_backslash_in_longer():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("abc" + single_backslash + single_backslash + "de")

    assert regex.test_string("abc" + single_backslash + "de")
    assert not regex.test_string("abc" + single_backslash + single_backslash + "de")


def test_open_bracket_alone():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse(single_backslash + "(")

    assert regex.test_string("(")
    assert not regex.test_string(single_backslash + "(")


def test_open_bracket_in_longer():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("abc" + single_backslash + "(de")

    assert regex.test_string("abc(de")
    assert not regex.test_string("abc" + single_backslash + "(de")


def test_close_bracket_alone():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse(single_backslash + ")")

    assert regex.test_string(")")
    assert not regex.test_string(single_backslash + ")")


def test_close_bracket_in_longer():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("abc" + single_backslash + ")de")

    assert regex.test_string("abc)de")
    assert not regex.test_string("abc" + single_backslash + ")de")


def test_escaped_brackets_in_star():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse(
        "abc(" + single_backslash + "()*de"
    )  # abc then as many open brackets as you like then de

    assert regex.test_string("abcde")
    assert regex.test_string("abc(de")
    assert regex.test_string("abc((de")
    assert regex.test_string("abc(((de")
    assert not regex.test_string("abc(e")
    assert not regex.test_string("abc" + single_backslash + "(de")


def test_new_line_alone():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("\n")

    assert regex.test_string("\n")
    assert not regex.test_string(single_backslash + "n")


def test_new_line_in_longer():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("abc\nabc")

    assert regex.test_string("abc\nabc")
    assert not regex.test_string("abc" + single_backslash + "nabc")


def test_tab_alone():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("\t")

    assert regex.test_string("\t")
    assert not regex.test_string(single_backslash + "t")


def test_tab_in_longer():
    single_backslash = chr(92)  # Doing this to be unambiguous about string escaping

    regex = Regex.parse("abc\tabc")

    assert regex.test_string("abc\tabc")
    assert not regex.test_string("abc" + single_backslash + "tabc")
