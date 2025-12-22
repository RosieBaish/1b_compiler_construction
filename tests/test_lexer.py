from lexer import Lexer, LexerError

import pytest


def test_lexer_notes():
    lexer = Lexer(
        [
            ("if", "IF"),
            ("then", "THEN"),
            ("[a-zA-Z]([a-zA-Z0-9])*", "IDENT"),
            ("[0-9]", "INT"),
            ("[ \t\n]", "SKIP"),
        ]
    )

    assert lexer.lex("if") == [("IF", "if")]
    assert lexer.lex("if ") == [("IF", "if"), ("SKIP", " ")]
    assert lexer.lex("if x then") == [
        ("IF", "if"),
        ("SKIP", " "),
        ("IDENT", "x"),
        ("SKIP", " "),
        ("THEN", "then"),
    ]

    with pytest.raises(LexerError) as le:
        lexer.lex("@")
    assert le.value.characters_consumed == 0

    with pytest.raises(LexerError) as le:
        lexer.lex("if@")
    assert le.value.characters_consumed == 2
