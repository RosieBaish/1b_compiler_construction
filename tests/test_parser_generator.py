from parser_generator import ParserGenerator

from grammar_reader import Grammar

# These are used in the eval but ruff doesn't know that
from common import NonTerminal, Terminal, Production, LR0_Accept, LR0_Shift, LR0_Reduce  # noqa: F401

# Ditto, used in exec
import abc  # noqa: F401

import ast
import pytest

##############################################################################################################
# WARNING
# This code uses exec and eval to check that the generated code is sensible
# On paper this is a terrible idea, however
# 1. This project is a compiler generator, so it already generates code that then gets executed
# 2. The resuting generated code then generates yet more code which will (hopefully) be executed
# So on balance, in the context of this project, it's OK.
# Or the whole project is a bad idea. Could go either way :-)
##############################################################################################################


def test_dict_to_string():
    test_dict = {
        0: 2,
        1: 3,
    }

    stringified_test_dict = {str(k): str(v) for k, v in test_dict.items()}

    python_source = ParserGenerator.dict_to_string(stringified_test_dict)

    print(python_source)

    assert ast.literal_eval(python_source) == test_dict


def test_terminals_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.terminals_to_string()

    assignment = "_T: list[Terminal] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.terminals


def test_nonterminals_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.nonterminals_to_string()

    assignment = "_N: list[NonTerminal] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.nonterminals


def test_productions_to_string():
    g = Grammar.from_file("slang.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    _T = g.terminals
    _N = g.nonterminals

    python_source = pg.productions_to_string()

    assignment = "_P: list[Production] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == pg.production_list


def test_action_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    _T = g.terminals
    _N = g.nonterminals
    _P = pg.production_list

    python_source = pg.action_to_string()

    assignment = "_Action: dict[int, dict[Terminal, Optional[LR0_Action]]] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == pg.cfg.slr1_action


def test_goto_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.goto_to_string()

    assignment = "_Goto: dict[int, dict[NonTerminal, Optional[int]]] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == pg.cfg.slr1_goto


def test_regexes_to_string():
    g = Grammar.from_file("slang.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.regexes_to_string()

    assignment = "_Regexes: list[tuple[Terminal, str, list[str]]] = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.terminal_triples


def test_generated_ast_classes():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.generate_ast_classes()

    print(python_source)

    expected_base_class = "GeneratedAST"
    expected_classes = ["S", "E", "T", "F"]

    namespace = {}
    exec(python_source, namespace)

    assert expected_base_class in namespace
    for c in expected_classes:
        assert c in namespace
        assert issubclass(namespace[c], namespace[expected_base_class])

    assert len(namespace.keys()) == 1 + len(expected_classes) + 1, (
        "+1 for base class, +1 for builtins"
    )


def test_generated_ast_classes_with_methods():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    g.optional_data = {
        "Class Methods": {
            "foo(self) -> str": {
                "E": "def foo(self) -> str:\n    return 'E'\n",
                "T": "def foo(self) -> str:\n    return 'T'\n",
            },
        }
    }
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.generate_ast_classes()

    print(python_source)

    expected_base_class = "GeneratedAST"
    expected_classes = ["S", "E", "T", "F"]
    expected_classes_with_methods = ["E", "T"]

    namespace = {"abc": abc}
    exec(python_source, namespace)

    assert expected_base_class in namespace
    for c in expected_classes:
        assert c in namespace
        assert issubclass(namespace[c], namespace[expected_base_class])

        assert hasattr(namespace[c], "foo")
        if c in expected_classes_with_methods:
            temp = namespace[c]([])
            assert temp.foo() == c
        else:
            with pytest.raises(NotImplementedError):
                temp = namespace[c]([])
                temp.foo()

    assert len(namespace.keys()) == 1 + len(expected_classes) + 2, (
        "+1 for base class, +1 for builtins and abc"
    )


def test_generated_semantic_actions():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.generate_ast_classes()
    print(python_source)

    namespace = {"_N": pg.g.nonterminals}
    exec("from common import NonTerminal; from typing import Any, Callable", namespace)

    exec(python_source, namespace)

    python_source = pg.generate_semantic_actions()
    assignment = "_semantic_actions: dict[NonTerminal, Callable[[list[Any]], Any]] = "
    assert python_source.startswith(assignment)

    print(python_source)

    exec(python_source, namespace)

    E = NonTerminal("E")

    assert isinstance(namespace["_semantic_actions"][E]([]), namespace["E"])
