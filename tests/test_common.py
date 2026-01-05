from common import Symbol, Terminal, NonTerminal


def test_not_equal():
    s = Symbol("x")
    t = Terminal("x")
    n = NonTerminal("x")

    assert s != t
    assert s != n
    assert t != n
