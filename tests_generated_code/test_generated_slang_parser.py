from generated_slang_parser import parse, ParseError, lex

from common import Terminal, dollar

import pytest


# NOTE: This uses the grammar in the file so Terminals are all upper case
def test_parse_id_times_id():
    assert (
        parse([Terminal("IDENT"), Terminal("MUL"), Terminal("IDENT"), dollar])
        == "EXPR(EXPR1(SUM(INTERMEDIATE_BINARY_OP(INTERMEDIATE_BINARY_OP(ASSIGNMENT(SIMPLE_EXPR(IDENT))), MUL, ASSIGNMENT(SIMPLE_EXPR(IDENT))))))"
    )


def test_parse_unexpected_token():
    with pytest.raises(ParseError) as e:
        parse([Terminal("IDENT"), Terminal("MUL"), Terminal("ADD"), dollar])
    assert e.value.message == "Unexpected token, unable to proceed"
    assert e.value.source_index == 2


def test_lexer():
    expected = [Terminal("IDENT", "x"), Terminal("MUL"), Terminal("IDENT", "y"), dollar]
    actual = lex("x * y")

    print(actual)
    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        assert e.identical_to(a)
