from generated_g2_parser import parse, ParseError, lex, E, T, F

from common import Terminal, dollar

import pytest

# NOTE: This uses the grammar in the file so Terminals are all upper case
ident = Terminal("ID")
times = Terminal("TIMES")
plus = Terminal("PLUS")
x = Terminal("ID", "x")
y = Terminal("ID", "y")


def test_parse_id():
    expected = E([T([F([ident])])])
    actual = parse([ident, dollar])

    assert len(expected.nodes) == len(actual.nodes) == 1
    expected_t = expected.nodes[0]
    actual_t = actual.nodes[0]

    assert len(expected_t.nodes) == len(actual_t.nodes) == 1
    expected_f = expected_t.nodes[0]
    actual_f = actual_t.nodes[0]

    assert len(expected_f.nodes) == len(actual_f.nodes) == 1
    assert expected_f.nodes[0] == ident
    assert actual_f.nodes[0] == ident

    assert expected_f == actual_f
    assert expected_t == actual_t
    assert expected == actual


def test_parse_id_times_id():
    assert parse([ident, times, ident, dollar]) == E(
        [T([T([F([ident])]), times, F([ident])])]
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
