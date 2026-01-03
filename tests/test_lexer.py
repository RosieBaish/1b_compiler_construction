from lexer import Lexer, LexerError

from cfg import Token

import pytest


def test_lexer_notes():
    lexer = Lexer(
        [
            (Token("IF"), "if", []),
            (Token("THEN"), "then", []),
            (Token("IDENT"), "[a-zA-Z]([a-zA-Z0-9])*", ["STORE"]),
            (Token("INT"), "[0-9]", ["STORE"]),
            (Token("SKIP"), "[ \t\n]", ["IGNORE"]),
        ]
    )

    assert lexer.lex("if") == [Token("IF")]
    assert lexer.lex("if ") == [Token("IF")]
    assert lexer.lex("if x then") == [
        Token("IF"),
        Token("IDENT"),
        Token("THEN"),
    ]
    assert lexer.lex("if x then")[1].identical_to(Token("IDENT", "x"))

    with pytest.raises(LexerError) as le:
        lexer.lex("@")
    assert le.value.characters_consumed == 0

    with pytest.raises(LexerError) as le:
        lexer.lex("if@")
    assert le.value.characters_consumed == 2
