from slang_ast import AST, Operator, Variable


from generated_slang_parser import parse, lex

import pytest


Unit = AST.Kind.Unit
What = AST.Kind.What
Var = AST.Kind.Var
Int = AST.Kind.Int
Bool = AST.Kind.Bool
UnaryOp = AST.Kind.UnaryOp
BinaryOp = AST.Kind.BinaryOp
If = AST.Kind.If
Pair = AST.Kind.Pair
Fst = AST.Kind.Fst
Snd = AST.Kind.Snd
Inl = AST.Kind.Inl
Inr = AST.Kind.Inr
Case = AST.Kind.Case
While = AST.Kind.While
Seq = AST.Kind.Seq
Ref = AST.Kind.Ref
Deref = AST.Kind.Deref
Assign = AST.Kind.Assign
Lambda = AST.Kind.Lambda
App = AST.Kind.App
LetFun = AST.Kind.LetFun


Add = Operator.Add
Mul = Operator.Mul
Div = Operator.Div
Sub = Operator.Sub
LessThan = Operator.LessThan
And = Operator.And
Or = Operator.Or
Eq = Operator.Eq
UnaryNegation = Operator.UnaryNegation
UnaryNot = Operator.UnaryNot


def ast_test_instances() -> list[tuple[str, AST]]:
    a_1 = AST(Int, [1])
    a_2 = AST(Int, [2])

    x = Variable("x")
    y = Variable("y")
    z = Variable("z")
    identity = Variable("identity")

    a_x = AST(Var, [x])
    a_y = AST(Var, [y])
    a_z = AST(Var, [z])

    a_true = AST(Bool, [True])
    a_false = AST(Bool, [False])

    return [
        ("()", AST(Unit, [])),
        ("?", AST(What, [])),
        ("x", a_x),
        ("10", AST(Int, [10])),
        ("true", a_true),
        ("- 10", AST(UnaryOp, [UnaryNegation, AST(Int, [10])])),
        ("~(true)", AST(UnaryOp, [UnaryNot, a_true])),
        ("1 + 1", AST(BinaryOp, [a_1, Add, a_1])),
        ("1 * 1", AST(BinaryOp, [a_1, Mul, a_1])),
        ("1 / 1", AST(BinaryOp, [a_1, Div, a_1])),
        ("1 - 1", AST(BinaryOp, [a_1, Sub, a_1])),
        ("1 < 1", AST(BinaryOp, [a_1, LessThan, a_1])),
        ("1 = 1", AST(BinaryOp, [a_1, Eq, a_1])),
        ("true || false", AST(BinaryOp, [a_true, Or, a_false])),
        ("True && False", AST(BinaryOp, [a_true, And, a_false])),
        ("True = False", AST(BinaryOp, [a_true, Eq, a_false])),
        ("if True then 1 else 2;", AST(If, [a_true, a_1, a_2])),
        ("(1, 2)", AST(Pair, [a_1, a_2])),
        ("x:=(1)", AST(Assign, [a_x, a_1])),
        ("x(y)", AST(App, [a_x, a_y])),
        ("fst ((1, 2))", AST(Fst, [AST(Pair, [a_1, a_2])])),
        ("snd ((1, 2))", AST(Snd, [AST(Pair, [a_1, a_2])])),
        ("inl int + int (1)", AST(Inl, [a_1])),
        ("inr int + int (2)", AST(Inr, [a_2])),
        ("ref (x)", AST(Ref, [a_x])),
        ("!(x)", AST(Deref, [a_x])),
        (
            "case x of inl (y: int) -> y | inr (z: int) -> z;",
            AST(Case, [a_x, y, a_y, z, a_z]),
        ),
        ("while true do x;", AST(While, [a_true, a_x])),
        ("begin x; y; z end", AST(Seq, [a_x, a_y, a_z])),
        ("fun (x:int) -> (x)", AST(Lambda, [x, a_x])),
        ("let x:int = 1 in (x)", AST(App, [AST(Lambda, [x, a_x]), a_1])),
        ("let identity (x:int): int = x in (x)", AST(LetFun, [identity, x, a_x, a_x])),
    ]


def test_str():
    assert str(AST(Var, [Variable("x")])) == "Var(x)"

    assert (
        str(AST(BinaryOp, [AST(Int, [1]), Add, AST(Int, [1])])) == "BinaryOp(1, Add, 1)"
    )


@pytest.mark.parametrize("source, ast", ast_test_instances())
def test_parse(source, ast):
    assert parse(lex(source)).to_AST() == ast


@pytest.mark.parametrize("_, ast", ast_test_instances())
def test_traverse_identify_eq(_, ast):
    assert ast.traverse(lambda x: x) == ast


def test_getattribute():
    x = AST(Var, [Variable("x")])
    y = AST(Var, [Variable("y")])
    z = AST(Var, [Variable("z")])

    ast = AST(Seq, [x, y, z])

    assert object.__getattribute__(ast, "sequence") == [x, y, z]

    assert getattr(ast, "sequence[0]") == AST(Var, [Variable("x")])
    assert getattr(ast, "sequence[1]") == AST(Var, [Variable("y")])
    assert getattr(ast, "sequence[2]") == AST(Var, [Variable("z")])


def test_getattribute_nested():
    x = Variable("x")
    y = Variable("y")
    z = Variable("z")

    a_x = AST(Var, [x])
    a_y = AST(Var, [y])
    a_z = AST(Var, [z])

    ast = AST(Case, [a_x, y, a_y, z, a_z])

    assert getattr(ast, "case_pairs[0]") == (y, a_y)
    assert getattr(ast, "case_pairs[1]") == (z, a_z)

    assert getattr(ast, "case_pairs[0][0]") == y
    assert getattr(ast, "case_pairs[0][1]") == a_y

    assert getattr(ast, "case_pairs[1][0]") == z
    assert getattr(ast, "case_pairs[1][1]") == a_z


def test_getattribute_invalid():
    invalid_case_attributes = [
        "case_pairs[",
        "case_pairs[]",
        "case_pairs]",
        "not_a_member",
        "case_select[0]",
        "case_pairs[0] [1]",
        "case_pairs [0]",
        "case_pairs[0] ",
    ]

    x = Variable("x")
    y = Variable("y")

    a_x = AST(Var, [x])
    a_y = AST(Var, [y])

    ast = AST(Case, [a_x, y, a_y, y, a_y])
    for attribute in invalid_case_attributes:
        with pytest.raises(AttributeError):
            getattr(ast, attribute)
