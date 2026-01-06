from enum import Enum, auto

from typing import Union


# Tragically I can't use @global_enum because mypy doesn't support it
class Operator(Enum):
    Add = (auto(), 2)
    Mul = (auto(), 2)
    Div = (auto(), 2)
    Sub = (auto(), 2)
    LessThan = (auto(), 2)
    And = (auto(), 2)
    Or = (auto(), 2)
    Eq = (auto(), 2)

    UnaryNegation = (auto(), 1)
    UnaryNot = (auto(), 1)
    UnaryRead = (auto(), 1)

    def __init__(self, _value: int, arity: int):
        self.arity = arity


class Variable:
    def __init__(self, name: str):
        self.name = name


class AST:
    class Kind(Enum):
        Unit = auto()
        What = auto()
        Var = auto()
        Int = auto()
        Bool = auto()
        UnaryOp = auto()
        BinaryOp = auto()
        If = auto()
        Pair = auto()
        Fst = auto()
        Snd = auto()
        Inl = auto()
        Inr = auto()
        Case = auto()
        While = auto()
        Seq = auto()
        Ref = auto()
        Deref = auto()
        Assign = auto()
        Lambda = auto()
        App = auto()
        LetFun = auto()
        LetRecFun = auto()

    def __init__(
        self, kind: Kind, operands: list[Union["AST", Operator, Variable, int, bool]]
    ):
        self.kind = kind
        match self.kind:
            case AST.Kind.Unit | AST.Kind.What:
                assert len(operands) == 0, operands
            case AST.Kind.Var:
                assert len(operands) == 1 and isinstance(operands[0], Variable), (
                    operands
                )
                self.variable = operands[0]
            case AST.Kind.Int:
                assert len(operands) == 1 and isinstance(operands[0], int), operands
                self.int_val = operands[0]
            case AST.Kind.Bool:
                assert len(operands) == 1 and isinstance(operands[0], bool), operands
                self.bool_val = operands[0]
            case AST.Kind.UnaryOp:
                assert (
                    len(operands) == 2
                    and isinstance(operands[0], Operator)
                    and operands[0].arity == 1
                    and isinstance(operands[1], AST)
                ), operands
                self.unary_op = operands[0]
                self.val = operands[1]
            case AST.Kind.BinaryOp:
                assert (
                    len(operands) == 3
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], Operator)
                    and operands[1].arity == 2
                    and isinstance(operands[2], AST)
                ), operands
                self.binary_op = operands[1]
                self.left = operands[0]
                self.right = operands[2]
            case AST.Kind.If:
                assert (
                    len(operands) == 3
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], AST)
                    and isinstance(operands[2], AST)
                ), operands
                self.condition = operands[0]
                self.true_branch = operands[1]
                self.false_branch = operands[2]
            case AST.Kind.Pair | AST.Kind.Assign | AST.Kind.App:
                assert (
                    len(operands) == 2
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], AST)
                ), operands
                self.left = operands[0]
                self.right = operands[1]
            case (
                AST.Kind.Fst
                | AST.Kind.Snd
                | AST.Kind.Inl
                | AST.Kind.Inr
                | AST.Kind.Ref
                | AST.Kind.Deref
            ):
                assert len(operands) == 1 and isinstance(operands[0], AST), operands
                self.val = operands[0]
            case AST.Kind.Case:
                assert (
                    len(operands) == 5
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], Variable)
                    and isinstance(operands[2], AST)
                    and isinstance(operands[3], Variable)
                    and isinstance(operands[4], AST)
                ), operands
                self.case_select = operands[0]
                self.case_pairs = [
                    (operands[1], operands[2]),
                    (operands[3], operands[4]),
                ]
            case AST.Kind.While:
                assert (
                    len(operands) == 2
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], AST)
                ), operands
                self.condition = operands[0]
                self.true_branch = operands[1]
            case AST.Kind.Seq:
                assert len(operands) > 0 and all(
                    isinstance(operand, AST) for operand in operands
                ), operands
                self.sequence = operands
            case AST.Kind.Lambda:
                assert (
                    len(operands) == 2
                    and isinstance(operands[0], Variable)
                    and isinstance(operands[1], AST)
                ), operands
                self.variable = operands[0]
                self.val = operands[1]
            case AST.Kind.LetFun | AST.Kind.LetRecFun:
                assert (
                    len(operands) == 4
                    and isinstance(operands[0], Variable)
                    and isinstance(operands[1], Variable)
                    and isinstance(operands[2], AST)
                    and isinstance(operands[3], AST)
                ), operands
                self.function_name = operands[0]
                self.variable = operands[1]
                self.val = operands[2]
                self.body = operands[3]
