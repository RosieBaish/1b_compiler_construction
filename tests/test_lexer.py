from lexer import Lexer, LexerError

from common import Terminal
from grammar_reader import Grammar

import pytest


def test_lexer_notes():
    lexer = Lexer(
        [
            (Terminal("IF"), "if", []),
            (Terminal("THEN"), "then", []),
            (Terminal("IDENT"), "[a-zA-Z]([a-zA-Z0-9])*", ["STORE"]),
            (Terminal("INT"), "[0-9]", ["STORE"]),
            (Terminal("SKIP"), "[ \t\n]", ["IGNORE"]),
        ]
    )

    assert lexer.lex("if") == [Terminal("IF")]
    assert lexer.lex("if ") == [Terminal("IF")]
    assert lexer.lex("if x then") == [
        Terminal("IF"),
        Terminal("IDENT"),
        Terminal("THEN"),
    ]
    assert lexer.lex("if x then")[1].identical_to(Terminal("IDENT", "x"))

    with pytest.raises(LexerError) as le:
        lexer.lex("@")
    assert le.value.characters_consumed == 0

    with pytest.raises(LexerError) as le:
        lexer.lex("if@")
    assert le.value.characters_consumed == 2


def test_lexer_slang_start_whitespace():
    backslash = "\\"
    assert len(backslash) == 1
    assert ord(backslash[0]) == 92

    g = Grammar.from_string(f"""
Grammar: SLang simplified 1

Terminals Start
WHITESPACE: "([ {backslash}n {backslash}t])*" IGNORE
IF: "if"
Terminals End

NonTerminals Start
EXPR
NonTerminals End

Productions Start
Productions End

Start Symbol: EXPR
""")

    print(g.terminal_triples)

    lexer = Lexer(g.terminal_triples)

    assert lexer.lex("\n\n\nif") == [Terminal("IF")]


def test_lexer_slang_prioritise_IF_over_IDENT():
    backslash = "\\"
    assert len(backslash) == 1
    assert ord(backslash[0]) == 92

    g = Grammar.from_string(f"""
Grammar: SLang simplified 2

Terminals Start
WHITESPACE: "([ {backslash}n {backslash}t])*" IGNORE
IF: "if"
IDENT: "[a-zA-Z]([a-zA-Z0-9_'])*" STORE
Terminals End

NonTerminals Start
EXPR
NonTerminals End

Productions Start
Productions End

Start Symbol: EXPR
""")

    print(g.terminal_triples)

    lexer = Lexer(g.terminal_triples)

    assert lexer.lex("\n\n\nif") == [Terminal("IF")]
