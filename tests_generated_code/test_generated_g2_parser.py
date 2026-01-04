from generated_g2_parser import parse, ParseError

from common import Terminal

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
