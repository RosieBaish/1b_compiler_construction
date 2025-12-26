from typing import Optional


class Token:
    def __init__(self, name: str, value: Optional[str] = None):
        self.name = name
        self.value = value

    def __str__(self) -> str:
        if self.value is not None:
            return f"{self.name}({self.value})"
        return self.name

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Token)
            and self.name == other.name
            and self.value == other.value
        )

    def __hash__(self) -> int:
        return hash((self.name, self.value))


class Symbol(Token):
    pass


class Terminal(Symbol):
    def __init__(self, name: str, value: Optional[str] = None):
        super().__init__(name, value)


class NonTerminal(Symbol):
    def __init__(self, name: str):
        super().__init__(name)


epsilon = Terminal("ε")


class CFG:
    def __init__(
        self,
        N: set[NonTerminal],
        T: set[Terminal],
        P: dict[NonTerminal, list[list[Symbol]]],
        E: NonTerminal,
    ):
        self.N = N
        self.T = T
        self.P = P
        self.E = E

        for n in self.N:
            assert n in self.P, n

        self.nullable: dict[NonTerminal, bool] = {}
        self.compute_nullable()

        self.first: dict[NonTerminal, set[Symbol]] = {n: set() for n in self.N}
        self.compute_first()

    def is_nullable(self, alpha: Symbol) -> bool:
        if isinstance(alpha, Terminal):
            assert alpha == epsilon or alpha in self.T, alpha
            return alpha == epsilon
        else:
            assert isinstance(alpha, NonTerminal) and alpha in self.N, alpha
            # If we don't know if n is nullable this will throw an exception
            # This is the correct behaviour because we use the exception for "have we computed it"
            return self.nullable[alpha]

    def compute_nullable(self) -> None:
        to_calculate = list(self.N)
        while len(to_calculate) > 0:
            prev_len = len(to_calculate)
            for n in list(to_calculate):
                # Note: n is a non terminal, not an int here despite convention
                productions = self.P[n]
                exception = False
                n_nullable = False  # We're going to OR this together in the loop
                for production in productions:
                    production_nullable = True  # We'll AND this together in the loop
                    try:
                        for alpha in production:
                            production_nullable &= self.is_nullable(alpha)
                            if not production_nullable:
                                break  # Short circuit
                    except Exception:
                        exception = True
                    n_nullable |= production_nullable
                    if n_nullable:  # Short circuit
                        break
                if not exception:
                    # We successfully checked every case, so put the result in the dict
                    self.nullable[n] = n_nullable
                    to_calculate.remove(n)
            assert len(to_calculate) < prev_len, "Made no progress"

    def print_nullable(self) -> None:  # pragma: no cover
        for n in self.N:
            print(f"Nullable({n}) = {self.nullable[n]}")

    def get_first(self, alpha: Symbol | list[Symbol]) -> set[Symbol]:
        if isinstance(alpha, Terminal):
            assert alpha == epsilon or alpha in self.T, alpha
            return {alpha}
        elif isinstance(alpha, NonTerminal):
            assert alpha in self.N, alpha
            return self.first[alpha]
        else:
            # Misnomer to call it alpha here when it's a list, but it's the only way
            assert isinstance(alpha, list), alpha
            first_set = self.get_first(alpha[0]) - {epsilon}
            if len(alpha) > 1 and self.is_nullable(alpha[0]):
                first_set |= self.get_first(alpha[1:])
            if all([self.is_nullable(a) for a in alpha]):
                first_set |= {epsilon}
            return first_set

    def compute_first(self) -> None:
        changed = True  # Initialise to True to get into the loop
        while changed:
            changed = False
            for n in self.N:
                new_first = set()
                for production in self.P[n]:
                    new_first |= self.get_first(production)
                if not new_first <= self.first[n]:
                    changed = True
                    self.first[n] |= new_first

    def print_first(self) -> None:  # pragma: no cover
        for n in self.N:
            print(f"First({n}) = {self.first[n]}")


def g3_prime() -> CFG:
    """This is G3' from the notes, see lecture 4 slide 5"""
    # Note that I had to use "variable" for "id" because that's a keyword in python

    S = NonTerminal("S")
    E = NonTerminal("E")
    E_prime = NonTerminal("E'")
    T = NonTerminal("T")
    T_prime = NonTerminal("T'")
    F = NonTerminal("F")

    plus = Terminal("+")
    times = Terminal("*")
    o_bracket = Terminal("(")
    c_bracket = Terminal(")")
    variable = Terminal("id")
    dollar = Terminal("$")

    return CFG(
        {S, E, E_prime, T, T_prime, F},
        {plus, times, o_bracket, c_bracket, variable, dollar},
        {
            S: [[E, dollar]],
            E: [[T, E_prime]],
            E_prime: [[plus, T, E_prime], [epsilon]],
            T: [[F, T_prime]],
            T_prime: [[times, F, T_prime], [epsilon]],
            F: [[o_bracket, E, c_bracket], [variable]],
        },
        S,
    )


def main() -> None:
    G3_prime = g3_prime()
    G3_prime.print_nullable()
    G3_prime.print_first()
