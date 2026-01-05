from parser_stub import parse_internal, ParseError, lex_internal

from cfg import CFG
from common import NonTerminal, Terminal, dollar

import pytest

E = NonTerminal("E")
T = NonTerminal("T")
F = NonTerminal("F")

ident = Terminal("id")
o_bracket = Terminal("(")
c_bracket = Terminal(")")
plus = Terminal("+")
times = Terminal("*")


def g2():
    P = {
        E: [[E, plus, T], [T]],
        T: [[T, times, F], [F]],
        F: [[ident], [o_bracket, E, c_bracket]],
    }

    return CFG(
        {E, T, F},
        {ident, o_bracket, c_bracket, plus, times},
        P,
        E,
        terminals_order=[o_bracket, ident, c_bracket, plus, times],
        nonterminals_order=[E, T, F],
        add_unique_starting_production=True,
    )


def test_g2_id_times_id():
    cfg = g2()

    semantic_actions = {
        n: lambda xs, n=n: f"{n}({', '.join([str(x) for x in xs])})" for n in cfg.N
    }

    assert (
        parse_internal(
            cfg.slr1_action,
            cfg.slr1_goto,
            semantic_actions,
            [ident, times, ident, dollar],
        )
        == "E(T(T(F(id)), *, F(id)))"
    )


def test_g2_unexpected_token():
    cfg = g2()

    semantic_actions = {
        n: lambda xs, n=n: f"{n}({', '.join([str(x) for x in xs])})" for n in cfg.N
    }

    with pytest.raises(ParseError) as e:
        parse_internal(
            cfg.slr1_action,
            cfg.slr1_goto,
            semantic_actions,
            [ident, times, plus, dollar],
        )
    assert e.value.message == "Unexpected token, unable to proceed"
    assert e.value.source_index == 2


def test_g2_lexer():
    Regexes = [
        (Terminal("WHITESPACE"), "([ \\n\\t])*", ["IGNORE"]),
        (Terminal("PLUS"), "+", []),
        (Terminal("TIMES"), "*", []),
        (Terminal("O_BRACKET"), "\\(", []),
        (Terminal("C_BRACKET"), "\\)", []),
        (Terminal("ID"), "[a-zA-Z]([a-zA-Z0-9_])*", ["STORE"]),
    ]

    expected = [Terminal("ID", "x"), Terminal("TIMES"), Terminal("ID", "y"), dollar]
    actual = lex_internal(Regexes, "x * y")

    print(actual)
    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        assert e.identical_to(a)
