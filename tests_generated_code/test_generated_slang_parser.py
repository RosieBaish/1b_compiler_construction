from generated_slang_parser import (
    parse,
    ParseError,
    lex,
    EXPR,
    EXPR1,
    SUM,
    INTERMEDIATE_BINARY_OP,
    ASSIGNMENT,
    SIMPLE_EXPR,
)

from common import Terminal, dollar

import pytest


ident = Terminal("IDENT")
times = Terminal("MUL")
plus = Terminal("ADD")
x = Terminal("IDENT", "x")
y = Terminal("IDENT", "y")


def test_parse_id_times_id():
    assert parse([ident, times, ident, dollar]) == EXPR(
        [
            EXPR1(
                [
                    SUM(
                        [
                            INTERMEDIATE_BINARY_OP(
                                [
                                    INTERMEDIATE_BINARY_OP(
                                        [ASSIGNMENT([SIMPLE_EXPR([ident])])]
                                    ),
                                    times,
                                    ASSIGNMENT([SIMPLE_EXPR([ident])]),
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


def test_parse_unexpected_token():
    with pytest.raises(ParseError) as e:
        parse([ident, times, plus, dollar])
    assert e.value.message == "Unexpected token, unable to proceed"
    assert e.value.source_index == 2


def test_lexer():
    expected = [x, times, y, dollar]
    actual = lex("x * y")

    print(actual)
    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        assert e.identical_to(a)
