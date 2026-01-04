from functools import total_ordering
from typing import Optional


@total_ordering
class Symbol:
    def __init__(self, name: str, value: Optional[str] = None):
        self.name = name
        self.value = value

    def identical_to(self, other: object) -> bool:
        return (
            isinstance(other, Symbol)
            and self.name == other.name
            and self.value == other.value
        )

    def __str__(self) -> str:
        if self.value is not None:
            return f"{self.name}({self.value})"
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Symbol) and self.name == other.name

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, Symbol)
        return self.name < other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Terminal(Symbol):
    def __init__(self, name: str, value: Optional[str] = None):
        super().__init__(name, value)


class NonTerminal(Symbol):
    def __init__(self, name: str):
        super().__init__(name)


class Production:
    def __init__(self, LHS: NonTerminal, RHS: list[Symbol]):
        self.LHS = LHS
        self.RHS = RHS

    def __getitem__(self, n: int) -> Symbol:
        return self.RHS[n]

    def __hash__(self) -> int:
        return hash((self.LHS, tuple(self.RHS)))

    def __str__(self) -> str:
        joiner = "" if all(len(str(s)) == 1 for s in self.RHS) else " "
        return f"{self.LHS} -> {joiner.join(str(r) for r in self.RHS)}"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Production)
            and self.LHS == other.LHS
            and self.RHS == other.RHS
        )

    def __len__(self) -> int:
        return len(self.RHS)


epsilon = Terminal("ε")
dollar = Terminal("$")
