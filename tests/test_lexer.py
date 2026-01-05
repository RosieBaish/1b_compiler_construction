from lexer import Lexer, LexerError

from common import Symbol
from grammar_reader import Grammar

import pytest


def test_lexer_notes():
    lexer = Lexer(
        [
            (Symbol("IF"), "if", []),
            (Symbol("THEN"), "then", []),
            (Symbol("IDENT"), "[a-zA-Z]([a-zA-Z0-9])*", ["STORE"]),
            (Symbol("INT"), "[0-9]", ["STORE"]),
            (Symbol("SKIP"), "[ \t\n]", ["IGNORE"]),
        ]
    )

    assert lexer.lex("if") == [Symbol("IF")]
    assert lexer.lex("if ") == [Symbol("IF")]
    assert lexer.lex("if x then") == [
        Symbol("IF"),
        Symbol("IDENT"),
        Symbol("THEN"),
    ]
    assert lexer.lex("if x then")[1].identical_to(Symbol("IDENT", "x"))

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

    assert lexer.lex("\n\n\nif") == [Symbol("IF")]


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

    assert lexer.lex("\n\n\nif") == [Symbol("IF")]
