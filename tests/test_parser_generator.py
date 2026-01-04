from parser_generator import ParserGenerator

from common import NonTerminal, Terminal, Production, LR0_Shift, LR0_Reduce, LR0_Accept

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


def test_action_to_string():
    a = Terminal("a")
    b = Terminal("b")

    A = NonTerminal("A")
    B = NonTerminal("B")

    # This Action table makes no sense, it's just a short one that has all the elements we need
    Action = {
        0: {
            a: [],
            b: [LR0_Shift(a, 1)],
        },
        1: {
            a: [LR0_Reduce(Production(A, [a, B, b]))],
            b: [LR0_Accept()],
        },
    }

    python_source = ParserGenerator.action_to_string(Action)

    assignment = "Action = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == Action


def test_goto_to_string():
    A = NonTerminal("A")
    B = NonTerminal("B")

    Goto = {
        0: {
            A: None,
            B: 1,
        },
        1: {
            A: 1,
            B: 0,
        },
    }

    python_source = ParserGenerator.goto_to_string(Goto)

    assignment = "Goto = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == Goto


def test_regexes_to_string():
    a = Terminal("a")
    b = Terminal("b")

    Regexes = [(a, "a", ["STORE"]), (b, "\n\t\\", ["IGNORE"])]

    python_source = ParserGenerator.regexes_to_string(Regexes)

    assignment = "Regexes = "
    assert python_source.startswith(assignment)
    python_source = python_source[len(assignment) :]

    print(python_source)

    assert eval(python_source) == Regexes
