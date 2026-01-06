from enum import Enum, auto

from typing import Any, Callable, Type, TypeVar, Union

T = TypeVar("T")


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

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


class Variable:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Variable) and self.name == other.name

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


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

        def __str__(self) -> str:
            return self.name

        def __repr__(self) -> str:
            return str(self)

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
                self.operator = operands[0]
                self.val = operands[1]
            case AST.Kind.BinaryOp:
                assert (
                    len(operands) == 3
                    and isinstance(operands[0], AST)
                    and isinstance(operands[1], Operator)
                    and operands[1].arity == 2
                    and isinstance(operands[2], AST)
                ), operands
                self.operator = operands[1]
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

    @property
    def child_names(self) -> list[tuple[str, Type]]:
        match self.kind:
            case AST.Kind.Unit | AST.Kind.What:
                return []
            case AST.Kind.Var:
                return [("variable", Variable)]
            case AST.Kind.Int:
                return [("int_val", int)]
            case AST.Kind.Bool:
                return [("bool_val", bool)]
            case AST.Kind.UnaryOp:
                return [("operator", Operator), ("val", AST)]
            case (
                AST.Kind.Fst
                | AST.Kind.Snd
                | AST.Kind.Inl
                | AST.Kind.Inr
                | AST.Kind.Ref
                | AST.Kind.Deref
            ):
                return [("val", AST)]
            case AST.Kind.BinaryOp:
                return [("left", AST), ("operator", Operator), ("right", AST)]
            case AST.Kind.Assign | AST.Kind.Pair | AST.Kind.App:
                return [("left", AST), ("right", AST)]
            case AST.Kind.If:
                return [("condition", AST), ("true_branch", AST), ("false_branch", AST)]
            case AST.Kind.While:
                return [("condition", AST), ("true_branch", AST)]
            case AST.Kind.Case:
                cases: list[tuple[str, Type]] = [("case_select", AST)]
                for i in range(len(self.case_pairs)):
                    cases.extend(
                        [
                            (f"case_pairs[{i}][0]", Variable),
                            (f"case_pairs[{i}][1]", AST),
                        ]
                    )
                return cases
            case AST.Kind.Lambda:
                return [("variable", Variable), ("val", AST)]
            case AST.Kind.Seq:
                return [(f"sequence[{i}]", AST) for i in range(len(self.sequence))]
            case AST.Kind.LetFun | AST.Kind.LetRecFun:
                return [
                    ("function_name", Variable),
                    ("variable", Variable),
                    ("val", AST),
                    ("body", AST),
                ]
        assert False, ("Unreachable", self)

    @property
    def child_node_names(self) -> list[str]:
        return [name for (name, type_) in self.child_names if type_ == AST]

    def traverse(self, func: Callable[["AST"], "AST"]) -> "AST":
        for node_name in self.child_node_names:
            prev_value = getattr(self, node_name)
            assert isinstance(prev_value, AST), prev_value
            new_value = prev_value.traverse(func)
            assert isinstance(new_value, AST), new_value
            setattr(self, node_name, new_value)
        return func(self)

    def traverse_to_value_single_leaf(
        self,
        leaf_func: Callable[[Variable | int | bool], T],
        func: Callable[[list[T]], T],
    ) -> T:
        new_children: list[T] = []
        for name, type_ in self.child_names:
            assert type_ in {AST, Operator, Variable, int, bool}, (name, type_)
            new_value: T
            if type_ == AST:
                prev_value = getattr(self, name)
                assert isinstance(prev_value, AST), (prev_value, type_)
                new_value = prev_value.traverse_to_value_single_leaf(leaf_func, func)
            else:
                prev_value = getattr(self, name)
                assert isinstance(prev_value, type_), (prev_value, type_)
                new_value = leaf_func(prev_value)
            new_children.append(new_value)
        return func(new_children)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AST):
            return False
        if self.kind != other.kind:
            return False
        if self.child_names != other.child_names:
            return False

        try:
            for name, type_ in self.child_names:
                c1 = getattr(self, name)
                c2 = getattr(other, name)
                if not isinstance(c1, type_) and isinstance(c2, type_):
                    return False
                if c1 != c2:
                    return False
        except AttributeError:
            return False

        return True

    def __str__(self) -> str:
        return f"{self.kind}({self.traverse_to_value_single_leaf(str, lambda xs: ', '.join(xs))})"

    def __repr__(self) -> str:
        return str(self)

    def __getattribute__(self, name: str) -> Any:
        """I want to be able to do getattr(foo, sequence[0]) to get the 0th member"""
        if name.count("[") != name.count("]"):
            raise AttributeError(f"Number of [ and ] didn't match in {name}")
        original_name = name
        brackets = ""
        if "[" in name:
            brackets = name[name.index("[") :]
            name = name[: name.index("[")]
        base_member_variable = object.__getattribute__(self, name)
        consumed = name
        while len(brackets) > 0:
            if brackets[0] != "[":
                raise AttributeError(
                    f"Expected [ next ({original_name}, {consumed}, {brackets}, {base_member_variable})"
                )
            close_index = brackets.index("]") + 1
            try:
                offset = int(brackets[1 : close_index - 1])
            except ValueError as ve:
                raise AttributeError(
                    (ve, original_name, consumed, brackets, base_member_variable)
                )
            consumed += brackets[:close_index]
            brackets = brackets[close_index:]
            try:
                base_member_variable = base_member_variable[offset]
            except TypeError as te:
                raise AttributeError(
                    (te, original_name, consumed, brackets, base_member_variable)
                )
        return base_member_variable
