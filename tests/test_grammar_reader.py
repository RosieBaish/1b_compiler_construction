from grammar_reader import Grammar

from cfg import Terminal, NonTerminal, epsilon
from regex import Regex


def test_basic():
    g = Grammar(
        contents="""
    Grammar: Basic 1

    Terminals Start
    a: "a"
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    A = NonTerminal("A")

    assert g.name == "Basic 1"
    assert g.terminals == [a]
    assert g.terminal_triples == [(a, Regex.parse("a"), [])]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a]]}
    assert g.start_symbol == A


def test_store():
    g = Grammar(
        contents="""
    Grammar: Basic 2

    Terminals Start
    a: "a"
    b: "b" STORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 2"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a]]}
    assert g.start_symbol == A


def test_multiple_productions_per_nonterminal():
    g = Grammar(
        contents="""
    Grammar: Basic 3

    Terminals Start
    a: "a"
    b: "b" STORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
       | b
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 3"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [b]]}
    assert g.start_symbol == A


def test_multiple_nonterminals():
    g = Grammar(
        contents="""
    Grammar: Basic 4

    Terminals Start
    a: "a"
    b: "b" STORE
    Terminals End

    NonTerminals Start
    A
    B
    NonTerminals End

    Productions Start
    A -> a
       | B
    B -> b
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")
    B = NonTerminal("B")

    assert g.name == "Basic 4"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["STORE"]),
    ]
    assert g.nonterminals == [A, B]
    assert g.productions == {A: [[a], [B]], B: [[b]]}
    assert g.start_symbol == A


def test_epsilon():
    g = Grammar(
        contents="""
    Grammar: Basic 5

    Terminals Start
    a: "a"
    b: "b" STORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
       | epsilon
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 5"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_ignore():
    g = Grammar(
        contents="""
    Grammar: Basic 6

    Terminals Start
    a: "a"
    b: "b" IGNORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
       | epsilon
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 6"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["IGNORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_read_from_file(tmp_path):
    tempfile = tmp_path / "basic_7.grammar"
    tempfile.write_text(
        """
    Grammar: Basic 7

    Terminals Start
    a: "a"
    b: "b" STORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
       | epsilon
    Productions End

    Start Symbol: A
    """,
        encoding="utf-8",
    )

    g = Grammar(filename=tempfile)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 7"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("a"), []),
        (b, Regex.parse("b"), ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_newline():
    """The grammar file should have a literal backslash and then a literal n as 2 separate characters
    The regex produced should just have a single newline character (ascii 10)"""
    backslash_n = "\\n"
    assert len(backslash_n) == 2
    assert ord(backslash_n[0]) == 92
    assert ord(backslash_n[1]) == 110

    g = Grammar(
        contents=f"""
    Grammar: Basic 8

    Terminals Start
    a: "{backslash_n}"
    b: "b" IGNORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> a
       | epsilon
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 8"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("\n"), []),
        (b, Regex.parse("b"), ["IGNORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_production_contains_token_not_token_name():
    g = Grammar(
        contents="""
    Grammar: Basic 8

    Terminals Start
    a: "foo"
    b: "b" IGNORE
    Terminals End

    NonTerminals Start
    A
    NonTerminals End

    Productions Start
    A -> foo
       | epsilon
    Productions End

    Start Symbol: A
    """
    )

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 8"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, Regex.parse("foo"), []),
        (b, Regex.parse("b"), ["IGNORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A
