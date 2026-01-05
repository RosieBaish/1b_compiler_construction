from parser_generator import ParserGenerator

from grammar_reader import Grammar

# These are used in the eval but ruff doesn't know that
from common import NonTerminal, Terminal, Production, LR0_Accept, LR0_Shift, LR0_Reduce  # noqa: F401


import ast

##############################################################################################################
# WARNING
# This code uses eval to check that the generated code is sensible
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

    assignment = "T = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.terminals


def test_nonterminals_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.nonterminals_to_string()

    assignment = "N = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.nonterminals


def test_productions_to_string():
    g = Grammar.from_file("slang.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    T = g.terminals
    N = g.nonterminals

    python_source = pg.productions_to_string()

    assignment = "P = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    _ = (
        T,
        N,
    )  # These are used in the eval, but the static analysis doesn't know that
    assert eval(python_source) == pg.production_list


def test_action_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    T = g.terminals
    N = g.nonterminals
    P = pg.production_list

    python_source = pg.action_to_string()

    assignment = "Action = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    _ = (
        T,
        N,
        P,
    )  # These are used in the eval, but the static analysis doesn't know that
    assert eval(python_source) == pg.cfg.slr1_action


def test_goto_to_string():
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.goto_to_string()

    assignment = "Goto = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == pg.cfg.slr1_goto


def test_regexes_to_string():
    g = Grammar.from_file("slang.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "", [], [])

    python_source = pg.regexes_to_string()

    assignment = "Regexes = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == g.terminal_triples
