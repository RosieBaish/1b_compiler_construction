from recursive_descent_parser_example import E, E_prime, T, T_prime, F

import pytest

# Not sure how best to test here
# I'll create a test case for each rule in the grammar
# And test that the subtrees correspond to the parses of the correct substrings


def test_E():
    e, cont = E.parse("x")
    assert isinstance(e, E)
    assert cont == ""
    assert e.t == T.parse("x")[0]
    assert e.e_prime == E_prime.parse("")[0]


def test_E_prime_plus():
    e_prime, cont = E_prime.parse("+y")
    assert isinstance(e_prime, E_prime)
    assert cont == ""
    assert e_prime.t == T.parse("y")[0]
    assert e_prime.e_prime == E_prime.parse("")[0]


def test_E_prime_epsilon():
    e_prime, cont = E_prime.parse("")
    assert e_prime.is_epsilon
    assert cont == ""


def test_T():
    t, cont = T.parse("x")
    assert isinstance(t, T)
    assert cont == ""
    assert t.f == F.parse("x")[0]
    assert t.t_prime == T_prime.parse("")[0]


def test_T_prime_plus():
    t_prime, cont = T_prime.parse("*y")
    assert isinstance(t_prime, T_prime)
    assert cont == ""
    assert t_prime.f == F.parse("y")[0]
    assert t_prime.t_prime == T_prime.parse("")[0]


def test_T_prime_epsilon():
    t_prime, cont = T_prime.parse("")
    assert t_prime.is_epsilon
    assert cont == ""


def test_F_id():
    f, cont = F.parse("x")
    assert isinstance(f, F)
    assert cont == ""
    assert f.is_id
    assert f.e is None
    assert f.token == "x"


def test_F_E():
    f, cont = F.parse("(x)")
    assert isinstance(f, F)
    assert cont == ""
    assert not f.is_id
    assert f.e == E.parse("x")[0]
    assert f.token is None


def test_F_error():
    """F expects either an id or an open bracket to start"""
    with pytest.raises(AssertionError):
        _ = F.parse("$")
