from string import printable

from nfa import NFA
from regex import Regex


def test_merged_nfas_empty():
    nfa = NFA.merge_nfas([])

    assert not nfa.test_string("")
    # Can't test any other strings because it has no alphabet


def test_merged_nfas_a_or_b():
    nfa1 = NFA(
        {"0", "1"},
        {"a", "b", "c"},
        lambda q, c: {"1"} if q == "0" and c == "a" else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "a"},
        state_rankings=["0", "1"],
    )
    nfa2 = NFA(
        {"0", "1"},
        {"a", "b", "c"},
        lambda q, c: {"1"} if q == "0" and c == "b" else set(),
        "0",
        {"1"},
        tags={"0": "0", "1": "b"},
        state_rankings=["0", "1"],
    )

    nfa = NFA.merge_nfas([nfa1, nfa2])

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "b"

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("ab")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("ba")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "b"

    nfa.test_string("cab")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_tag is None


def test_merged_nfas_untagged_a_or_b():
    nfa1 = NFA(
        {"0", "1"},
        {"a", "b", "c"},
        lambda q, c: {"1"} if q == "0" and c == "a" else set(),
        "0",
        {"1"},
    )
    nfa2 = NFA(
        {"0", "1"},
        {"a", "b", "c"},
        lambda q, c: {"1"} if q == "0" and c == "b" else set(),
        "0",
        {"1"},
    )

    nfa = NFA.merge_nfas([nfa1, nfa2])

    assert not nfa.test_string("")
    assert nfa.test_string("a")
    assert nfa.test_string("b")
    assert not nfa.test_string("aa")
    assert not nfa.test_string("ab")
    assert not nfa.test_string("ba")


def test_merged_nfas_from_tagged_regexes_a_or_b():
    Sigma = {"a", "b", "c"}
    nfa1 = NFA.from_regex(Regex.parse("a"), Sigma, accept_tag="a")
    nfa2 = NFA.from_regex(Regex.parse("b"), Sigma, accept_tag="b")
    nfa = NFA.merge_nfas([nfa1, nfa2])

    nfa.test_string("")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_tag is None

    nfa.test_string("a")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("b")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "b"

    nfa.test_string("aa")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("ab")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "a"

    nfa.test_string("ba")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "b"

    nfa.test_string("cab")
    assert nfa.num_chars_accepted == 0
    assert nfa.last_accept_tag is None


def test_merged_nfas_from_tagged_regexes_notes():
    regexes = [
        ("if", "IF"),
        ("then", "THEN"),
        ("[a-zA-Z]([a-zA-Z0-9])*", "IDENT"),
        ("[0-9]", "INT"),
        ("[ \t\n]", "SKIP"),
    ]
    nfas = [
        NFA.from_regex(Regex.parse(r), set(printable), accept_tag=t)
        for (r, t) in regexes
    ]
    nfa = NFA.merge_nfas(nfas)

    nfa.test_string("if")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_tag == "IF"

    nfa.test_string("ifx")
    assert nfa.num_chars_accepted == 3
    assert nfa.last_accept_tag == "IDENT"

    nfa.test_string("if ")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_tag == "IF"

    nfa.test_string("if ifx")
    assert nfa.num_chars_accepted == 2
    assert nfa.last_accept_tag == "IF"

    nfa.test_string("then if")
    assert nfa.num_chars_accepted == 4
    assert nfa.last_accept_tag == "THEN"

    nfa.test_string(" if")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "SKIP"

    nfa.test_string("\tif")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "SKIP"

    nfa.test_string("\nif")
    assert nfa.num_chars_accepted == 1
    assert nfa.last_accept_tag == "SKIP"
