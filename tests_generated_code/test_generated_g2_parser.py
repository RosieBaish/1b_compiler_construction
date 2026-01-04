from generated_g2_parser import parse, ParseError, lex

from common import Terminal, dollar

import pytest


# NOTE: This uses the grammar in the file so Terminals are all upper case
def test_parse_id_times_id():
    assert (
        parse([Terminal("ID"), Terminal("TIMES"), Terminal("ID"), Terminal("$")])
        == "E(T(T(F(ID)), TIMES, F(ID)))"
    )


def test_parse_unexpected_token():
    with pytest.raises(ParseError) as e:
        parse([Terminal("ID"), Terminal("TIMES"), Terminal("PLUS"), Terminal("$")])
    assert e.value.message == "Unexpected token, unable to proceed"
    assert e.value.source_index == 2


def test_lexer():
    expected = [Terminal("ID", "x"), Terminal("TIMES"), Terminal("ID", "y"), dollar]
    actual = lex("x * y")

    print(actual)
    assert len(expected) == len(actual)
    for e, a in zip(expected, actual):
        assert e.identical_to(a)
