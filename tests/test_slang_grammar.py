from grammar_reader import Grammar

from cfg import CFG
from common import Terminal
from lexer import Lexer


def test_terminals():
    g = Grammar(filename="slang.grammar")

    # Everything from lexer.mll in the slang repo except comments
    expected_terminal_names = [
        "WHITESPACE",
        "LPAREN",
        "RPAREN",
        "COMMA",
        "COLON",
        "SEMICOLON",
        "ADD",
        "SUB",
        "MUL",
        "DIV",
        "NOT",
        "EQUAL",
        "ASSIGN",
        "LT",
        "ANDOP",
        "OROP",
        "BAR",
        "ARROW",
        "WHAT",
        "BANG",
        "UNIT",
        "TRUE",
        "FALSE",
        "REF",
        "INL",
        "INR",
        "FST",
        "SND",
        "CASE",
        "OF",
        "IF",
        "THEN",
        "ELSE",
        "LET",
        "FUN",
        "IN",
        "BEGIN",
        "END",
        "WHILE",
        "DO",
        "BOOL",
        "INTTYPE",
        "UNITTYPE",
        "INT",
        "IDENT",
    ]

    expected_terminals = [Terminal(name) for name in expected_terminal_names]

    for terminal in expected_terminals:
        assert terminal in g.terminals
    for terminal in g.terminals:
        assert terminal in expected_terminals


def test_lex():
    g = Grammar(filename="slang.grammar")

    lexer = Lexer(g.terminal_triples)

    # Example if.slang from the slang repo
    if_slang = """


if ? = 0 then 17 else 21
    """

    expected = [
        Terminal("IF"),
        Terminal("WHAT"),
        Terminal("EQUAL"),
        Terminal("INT", "0"),
        Terminal("THEN"),
        Terminal("INT", "17"),
        Terminal("ELSE"),
        Terminal("INT", "21"),
    ]

    actual = lexer.lex(if_slang)

    print(expected)
    print()
    print(actual)
    print()

    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        assert e.identical_to(a)


def test_cfg_created_successfully():
    g = Grammar(filename="slang.grammar")

    assert isinstance(g.cfg, CFG)
