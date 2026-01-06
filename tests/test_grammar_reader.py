from grammar_reader import Grammar

from cfg import CFG
from common import Terminal, NonTerminal, epsilon


def test_basic():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    A = NonTerminal("A")

    assert g.name == "Basic 1"
    assert g.terminals == [a]
    assert g.terminal_triples == [(a, "a", [])]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a]]}
    assert g.start_symbol == A


def test_store():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 2"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a]]}
    assert g.start_symbol == A


def test_multiple_productions_per_nonterminal():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 3"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [b]]}
    assert g.start_symbol == A


def test_multiple_nonterminals():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")
    B = NonTerminal("B")

    assert g.name == "Basic 4"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["STORE"]),
    ]
    assert g.nonterminals == [A, B]
    assert g.productions == {A: [[a], [B]], B: [[b]]}
    assert g.start_symbol == A


def test_epsilon():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 5"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["STORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_ignore():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 6"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["IGNORE"]),
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

    g = Grammar.from_file(tempfile)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 7"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "a", []),
        (b, "b", ["STORE"]),
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

    g = Grammar.from_string(f"""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 8"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "\n", []),
        (b, "b", ["IGNORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_production_contains_token_not_token_name():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    b = Terminal("b")
    A = NonTerminal("A")

    assert g.name == "Basic 8"
    assert g.terminals == [a, b]
    assert g.terminal_triples == [
        (a, "foo", []),
        (b, "b", ["IGNORE"]),
    ]
    assert g.nonterminals == [A]
    assert g.productions == {A: [[a], [epsilon]]}
    assert g.start_symbol == A


def test_cfg():
    g = Grammar.from_string("""
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
    """)

    a = Terminal("a")
    A = NonTerminal("A")

    assert g.name == "Basic 1"
    assert isinstance(g.cfg, CFG)
    assert g.cfg == CFG({A}, {a}, {A: [[a]]}, A)


def test_parse_raw_section():
    source = """
Test source \n
    More random stuff \t
"""

    lines = ["Start\n"] + source.split("\n") + ["End\n", "trailing stuff\n"]

    assert Grammar.parse_raw_section(lines, "Start", "End") == (
        source,
        len(lines) - 1,
    )


def test_parse_raw_section_empty():
    lines = ["A\n", "B\n", "trailing stuff\n"]

    assert Grammar.parse_raw_section(lines, "A", "B") == ("", 2)


def test_parse_class_methods_empty():
    lines = ["Class Methods Start\n", "Class Methods End\n"]

    assert Grammar.parse_class_methods(lines) == ({}, 2)


def test_parse_class_methods_blank():
    lines = ["Class Methods Start\n", "\n", "Class Methods End\n"]

    assert Grammar.parse_class_methods(lines) == ({}, 3)


def test_parse_class_methods_single_method_and_class():
    source = """
Class Methods Start
Method Start foo
Class Start bar
[code goes here]
Class End bar
Method End foo
Class Methods End
Trailing Stuff""".lstrip()

    lines = source.split("\n")

    print(lines)

    assert Grammar.parse_class_methods(lines) == (
        {"foo": {"bar": "[code goes here]\n"}},
        len(lines) - 1,
    )


def test_parse_class_methods_multiple_method_and_class():
    source = """
Class Methods Start
Method Start foo
Class Start bar
[code goes here]
Class End bar
Class Start baz
Class End baz
Method End foo
Method Start foo2
Method End foo2
Class Methods End
Trailing Stuff""".lstrip()

    lines = source.split("\n")

    print(lines)

    assert Grammar.parse_class_methods(lines) == (
        {"foo": {"bar": "[code goes here]\n", "baz": ""}, "foo2": {}},
        len(lines) - 1,
    )


def test_parse_optional_data_prefix():
    source = """
Prefix Start
"This is a prefix"
Prefix End


"""
    lines = source.split("\n")

    assert Grammar.parse_optional_data(lines) == {"Prefix": '"This is a prefix"\n'}


def test_parse_optional_data_class_methods():
    source = """


Class Methods Start
Method Start foo
Class Start bar
[code goes here]
Class End bar
Class Start baz
Class End baz
Method End foo
Method Start foo2
Method End foo2
Class Methods End
"""

    lines = source.split("\n")

    print(lines)

    assert Grammar.parse_optional_data(lines) == {
        "Class Methods": {"foo": {"bar": "[code goes here]\n", "baz": ""}, "foo2": {}},
    }


def test_grammars_have_optional_data():
    slang = Grammar.from_file("slang.grammar")
    g2 = Grammar.from_file("g2.grammar")

    assert slang.optional_data != {}
    assert g2.optional_data == {}
