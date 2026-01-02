from functools import total_ordering
from typing import Optional


@total_ordering
class Token:
    def __init__(self, name: str, value: Optional[str] = None):
        self.name = name
        self.value = value

    def identical_to(self, other: object) -> bool:
        return (
            isinstance(other, Token)
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
        return isinstance(other, Token) and self.name == other.name

    def __lt__(self, other: object) -> bool:
        assert isinstance(other, Token)
        return self.name < other.name

    def __hash__(self) -> int:
        return hash(self.name)


class Symbol(Token):
    pass


class Terminal(Symbol):
    def __init__(self, name: str, value: Optional[str] = None):
        super().__init__(name, value)


class NonTerminal(Symbol):
    def __init__(self, name: str):
        super().__init__(name)


class Production:  # pragma: no cover
    def __init__(self, LHS: NonTerminal, RHS: list[Symbol]):
        self.LHS = LHS
        self.RHS = RHS

    def __getitem__(self, n: int) -> Symbol:
        return self.RHS[n]

    def __hash__(self) -> int:
        return hash((self.LHS, tuple(self.RHS)))

    def __str__(self) -> str:
        return f"{self.LHS} -> {''.join(str(r) for r in self.RHS)}"

    def __repr__(self) -> str:
        return str(self)


epsilon = Terminal("ε")
dollar = Terminal("$")


class CFG:
    def __init__(
        self,
        N: set[NonTerminal],
        T: set[Terminal],
        P: dict[NonTerminal, list[list[Symbol]]],
        E: NonTerminal,
        terminals_order: Optional[list[Terminal]] = None,
        nonterminals_order: Optional[list[NonTerminal]] = None,
        nullable_hints: dict[NonTerminal, bool] = {},
    ):
        self.N = N
        self.T = T

        self.P: dict[NonTerminal, list[Production]] = {n: [] for n in self.N}
        for n, productions in P.items():
            for production in productions:
                self.P[n].append(Production(n, production))
        self.E = E

        self.terminals_order = terminals_order
        self.nonterminals_order = nonterminals_order

        for n in self.N:
            assert n in self.P, n

        self._computed_nullable = False
        self._nullable: dict[NonTerminal, bool] = {}
        self._nullable_hints = nullable_hints

        self._computed_first = False
        self._first: dict[NonTerminal, set[Terminal]] = {n: set() for n in self.N}

        self._computed_follow = False
        self._follow: dict[NonTerminal, set[Terminal]] = {n: set() for n in self.N}

        self._computed_ll1_parse_table = False
        self._ll1_parse_table: dict[NonTerminal, dict[Terminal, set[Production]]] = {
            n: {t: set() for t in self.T} for n in self.N
        }

    def __str__(self) -> str:
        all_prods = []
        for k, v in self.P.items():
            all_prods.extend(v)
        return f"<{self.N}, {self.T}, {all_prods}, {self.E}>"

    def __repr__(self) -> str:
        return str(self)

    def is_left_recursive(self) -> bool:
        """Returns true iff the grammar has a rule A -> αAβ for some nullable α"""

        for A, productions in self.P.items():
            for production in productions:
                for symbol in production.RHS:
                    if symbol == A:
                        return True
                    if not self.is_nullable(symbol):
                        break
        return False

    def is_right_recursive(self) -> bool:
        """Returns true iff the grammar has a rule A -> αAβ for some nullable β"""

        for A, productions in self.P.items():
            for production in productions:
                for symbol in production.RHS[::-1]:
                    if symbol == A:
                        return True
                    if not self.is_nullable(symbol):
                        break
        return False

    def is_nullable(self, alpha: Symbol) -> bool:
        if isinstance(alpha, Terminal):
            assert alpha == epsilon or alpha in self.T, alpha
            return alpha == epsilon
        else:
            assert isinstance(alpha, NonTerminal) and alpha in self.N, alpha
            # If we don't know if n is nullable this will throw an exception
            # This is the correct behaviour because we use the exception for "have we computed it"
            return self.nullable[alpha]

    @property
    def nullable(self) -> dict[NonTerminal, bool]:
        # In theory you can do this without the hints
        # But if you have productions which can go to themselves
        # (because everything left of the symbol is nullable)
        # e.g. S -> XYS|c where X and Y are nullable
        # Then this code can't figure it out
        # Because it gets stuck in an infinite loop of nullable(S) iff nullable(S)
        # So in those cases give a hint for that symbol
        # It's ugly and I hate it but it's better than nothing
        # I think the correct answer is to just exclude the problematic production
        # But I've not proved that point

        if self._computed_nullable:
            return self._nullable

        # We haven't fully computed it yet, but we use the partially computed version
        # In the calculation so we need to not just be in an infinite loop
        self._computed_nullable = True

        for k, v in self._nullable_hints.items():
            self._nullable[k] = v

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
                        for alpha in production.RHS:
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
                    self._nullable[n] = n_nullable
                    to_calculate.remove(n)
            assert len(to_calculate) < prev_len, (to_calculate, "Made no progress")

        return self._nullable

    def print_nullable(self) -> None:  # pragma: no cover
        for n in (
            sorted(list(self.N))
            if self.nonterminals_order is None
            else self.nonterminals_order
        ):
            print(f"Nullable({n}) = {self.nullable[n]}")

    def get_first(self, alpha: Symbol | list[Symbol] | Production) -> set[Terminal]:
        if isinstance(alpha, Terminal):
            assert alpha == epsilon or alpha in self.T, alpha
            return {alpha}
        elif isinstance(alpha, NonTerminal):
            assert alpha in self.N, alpha
            return self.first[alpha]
        elif isinstance(alpha, Production):
            return self.get_first(alpha.RHS)
        else:
            # Misnomer to call it alpha here when it's a list, but it's the only way
            assert isinstance(alpha, list), alpha
            if len(alpha) == 0:
                return set()
            first_set = self.get_first(alpha[0]) - {epsilon}
            if len(alpha) > 1 and self.is_nullable(alpha[0]):
                first_set |= self.get_first(alpha[1:])
            if all([self.is_nullable(a) for a in alpha]):
                first_set |= {epsilon}
            return first_set

    @property
    def first(self) -> dict[NonTerminal, set[Terminal]]:
        if self._computed_first:
            return self._first

        # We haven't fully computed it yet, but we use the partially computed version
        # In the calculation so we need to not just be in an infinite loop
        self._computed_first = True

        changed = True  # Initialise to True to get into the loop
        while changed:
            changed = False
            for n in self.N:
                new_first = set()
                for production in self.P[n]:
                    new_first |= self.get_first(production)
                if not new_first <= self._first[n]:
                    changed = True
                    self._first[n] |= new_first

        return self._first

    def print_first(self) -> None:  # pragma: no cover
        for n in (
            sorted(list(self.N))
            if self.nonterminals_order is None
            else self.nonterminals_order
        ):
            print(f"First({n}) = {self.first[n]}")

    @property
    def follow(self) -> dict[NonTerminal, set[Terminal]]:
        # As a nice little efficiency win, do this in 2 stages
        # Figure out what the fixed point dependencies are, and get all the first sets
        # Then do the fixed point computation

        if self._computed_follow:
            return self._follow

        fixed_point_dependencies: dict[NonTerminal, set[NonTerminal]] = {
            n: set() for n in self.N
        }

        self._follow[self.E] = {dollar}

        for n in self.N:
            for production in self.P[n]:
                for i, A in enumerate(production.RHS):
                    if not isinstance(A, NonTerminal):
                        continue
                    beta = production.RHS[i + 1 :]
                    self._follow[A] |= self.get_first(beta) - {epsilon}
                    beta_nullable = all([self.is_nullable(b) for b in beta])

                    if len(beta) == 0 or beta_nullable:
                        fixed_point_dependencies[A] |= {n}

        changed = True  # Initialise to True to get into the loop
        while changed:
            changed = False
            for n in self.N:
                new_follow: set[Terminal] = set()
                for non_terminal in fixed_point_dependencies[n]:
                    new_follow |= self._follow[non_terminal]
                if not new_follow <= self._follow[n]:
                    changed = True
                    self._follow[n] |= new_follow

        self._computed_follow = True
        return self._follow

    def print_follow(self) -> None:  # pragma: no cover
        for n in (
            sorted(list(self.N))
            if self.nonterminals_order is None
            else self.nonterminals_order
        ):
            print(f"Follow({n}) = {self.follow[n]}")

    @property
    def ll1_parse_table(self) -> dict[NonTerminal, dict[Terminal, set[Production]]]:
        if self._computed_ll1_parse_table:
            return self._ll1_parse_table

        # We could assert here that the grammar isn't left recursive
        # However you can still generate a parse table for some left recursive grammars, you just can't parse with it
        # So given that our goal here is education not creating tools, let's allow that case

        for A, productions in self.P.items():
            for production in productions:
                for a in self.get_first(production):
                    if a == epsilon:
                        for b in self.follow[A]:
                            self._ll1_parse_table[A][b] |= {production}
                    else:
                        self._ll1_parse_table[A][a] |= {production}

        self._computed_ll1_parse_table = True
        return self._ll1_parse_table

    def print_ll1_parse_table(self) -> None:  # pragma: no cover
        terminals = (
            sorted(list(self.T))
            if self.terminals_order is None
            else self.terminals_order
        )
        nonterminals = (
            sorted(list(self.N))
            if self.nonterminals_order is None
            else self.nonterminals_order
        )

        rows: list[list[str]] = []
        rows.append([""] + [str(t) for t in terminals])
        longest_production = max([len(t) for t in rows[0]])

        for n in nonterminals:
            row = [str(n)]
            for t in terminals:
                prods = self.ll1_parse_table[n][t]
                prod_strings = sorted(
                    ["".join([str(s) for s in prod.RHS]) for prod in list(prods)]
                )
                if len(prods) == 0:
                    row.append("")
                elif len(prods) == 1:
                    row.append("".join([s for s in prod_strings[0]]))
                else:
                    row.append(f"{{{', '.join(prod_strings)}}}")
            longest_production = max(longest_production, max([len(p) for p in row]))
            rows.append(row)
        row_strings = [
            "|".join([f" {s:{longest_production}} " for s in row]) for row in rows
        ]
        row_len = len(row_strings[0])
        assert all([len(r) == row_len for r in row_strings]), row_strings

        print(("\n" + "-" * row_len + "\n").join(row_strings))


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
        terminals_order=[variable, plus, times, o_bracket, c_bracket, dollar],
        nonterminals_order=[S, E, E_prime, T, T_prime, F],
    )


def main() -> None:
    G3_prime = g3_prime()
    G3_prime.print_nullable()
    print()
    G3_prime.print_first()
    print()
    G3_prime.print_follow()
    print()
    G3_prime.print_ll1_parse_table()
