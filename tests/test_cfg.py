from cfg import CFG, g3_prime
from common import (
    dollar,
    epsilon,
    NonTerminal,
    Terminal,
    Production,
    LR0_Accept,
    LR0_Shift,
    LR0_Reduce,
)


def test_G3_prime_nullable_nonterminals():
    G3_prime = g3_prime()

    # Expected values hand-computed in my notes
    expected_values = {
        "F": False,
        "T'": True,
        "T": False,
        "E'": True,
        "E": False,
        "S": False,
    }
    G3_prime.print_nullable()

    for n in G3_prime.N:
        assert G3_prime.is_nullable(n) == expected_values[n.name], n


def test_G3_prime_nullable_other():
    G3_prime = g3_prime()

    E_prime = NonTerminal("E'")
    T = NonTerminal("T")
    T_prime = NonTerminal("T'")

    plus = Terminal("+")

    expected_values = [
        (plus, False),
        (epsilon, True),
        ([plus, T, E_prime], False),
        ([epsilon], True),
        ([E_prime, T_prime], True),
        (Production(E_prime, [epsilon]), True),
    ]

    for val, answer in expected_values:
        assert G3_prime.is_nullable(val) == answer


def test_epsilon_equivalence():
    e = Terminal("ε")
    assert e == epsilon


def test_G3_prime_first():
    G3_prime = g3_prime()

    plus = Terminal("+")
    times = Terminal("*")
    o_bracket = Terminal("(")
    variable = Terminal("id")

    # Expected values hand-computed in my notes
    expected_values = {
        "F": {o_bracket, variable},
        "T'": {times, epsilon},
        "T": {o_bracket, variable},
        "E'": {plus, epsilon},
        "E": {o_bracket, variable},
        "S": {o_bracket, variable},
    }
    G3_prime.print_first()

    for n in G3_prime.N:
        assert G3_prime.get_first(n) == expected_values[n.name], n


def test_nullable_first_symbol():
    """
    Simple case where S can be:
    - id2 (via S -> E T -> ε T -> T -> id2)
    - id1 id2 (via S -> ET -> id1 T -> id1 id2)
    so First(S) should be {id1, id2} if the nullable stuff works properly
    """
    S = NonTerminal("S")
    E = NonTerminal("E")
    T = NonTerminal("T")

    variable1 = Terminal("id1")
    variable2 = Terminal("id2")

    cfg = CFG(
        {S, E, T},
        {variable1, variable2},
        {
            S: [[E, T]],
            E: [[variable1], [epsilon]],
            T: [[variable2]],
        },
        S,
    )

    expected_values = {
        "S": {variable1, variable2},
        "E": {epsilon, variable1},
        "T": {variable2},
    }

    cfg.print_first()

    for n in cfg.N:
        assert cfg.get_first(n) == expected_values[n.name], n


def test_G3_prime_follow():
    G3_prime = g3_prime()

    plus = Terminal("+")
    times = Terminal("*")
    c_bracket = Terminal(")")

    # Expected values hand-computed in my notes
    expected_values = {
        "S": {dollar},
        "E": {dollar, c_bracket},
        "E'": {dollar, c_bracket},
        "T": {plus, dollar, c_bracket},
        "T'": {plus, dollar, c_bracket},
        "F": {times, plus, dollar, c_bracket},
    }
    G3_prime.print_follow()

    for n in G3_prime.N:
        assert G3_prime.follow[n] == expected_values[n.name], n


def test_G3_prime_ll1_parse_table():
    G3_prime = g3_prime()

    expected_values = {
        "S": {"id": ["E$"], "(": ["E$"]},
        "E": {"id": ["T E'"], "(": ["T E'"]},
        "E'": {"+": ["+ T E'"], ")": ["ε"], "$": ["ε"]},
        "T": {"id": ["F T'"], "(": ["F T'"]},
        "T'": {"+": ["ε"], "*": ["* F T'"], ")": ["ε"], "$": ["ε"]},
        "F": {"id": ["id"], "(": ["(E)"]},
    }

    G3_prime.print_ll1_parse_table()

    for n in G3_prime.N:
        for t in G3_prime.T:
            if str(t) in expected_values[str(n)]:
                prods = G3_prime.ll1_parse_table[n][t]
                expected_prods = [
                    f"{n} -> {v}" for v in expected_values[str(n)][str(t)]
                ]
                assert len(prods) == len(expected_prods)
                for prod in prods:
                    assert str(prod) in expected_prods
            else:
                assert G3_prime.ll1_parse_table[n][t] == set()


def test_ambiguous_grammar():
    """The non-ll(s) from lecture 4 slide 23(80)"""
    S_prime = NonTerminal("S'")  # Needed so we can have $ as end of input

    S = NonTerminal("S")
    X = NonTerminal("X")
    Y = NonTerminal("Y")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    dollar = Terminal("$")  # Not in the notes

    cfg = CFG(
        {S_prime, S, X, Y},
        {a, b, c, dollar},
        {
            S_prime: [[S, dollar]],
            S: [[X, Y, S], [a]],
            X: [[Y], [b]],
            Y: [[c], [epsilon]],
        },
        S_prime,
    )

    expected_nullable = {
        "S'": False,
        "S": False,
        "X": True,
        "Y": True,
    }
    cfg.print_nullable()

    for n in cfg.N:
        assert cfg.is_nullable(n) == expected_nullable[n.name], n

    expected_firsts = {
        "S'": {a, b, c},
        "S": {a, b, c},
        "X": {b, c, epsilon},
        "Y": {c, epsilon},
    }

    cfg.print_first()

    for n in cfg.N:
        assert cfg.get_first(n) == expected_firsts[n.name], n

    expected_follows = {
        "S'": {dollar},
        "S": {dollar},
        "X": {a, b, c},
        "Y": {a, b, c},
    }

    cfg.print_follow()

    for n in cfg.N:
        assert cfg.follow[n] == expected_follows[n.name], n

    expected_ll1_parse_table = {
        "S'": {"a": ["S$"], "b": ["S$"], "c": ["S$"]},
        "S": {"a": ["XYS", "a"], "b": ["XYS"], "c": ["XYS"]},
        "X": {"a": ["Y"], "b": ["Y", "b"], "c": ["Y"]},
        "Y": {"a": ["ε"], "b": ["ε"], "c": ["ε", "c"]},
    }

    cfg.print_ll1_parse_table()

    for n in cfg.N:
        for t in cfg.T:
            if str(t) in expected_ll1_parse_table[str(n)]:
                prods = cfg.ll1_parse_table[n][t]
                expected_prods = [
                    f"{n} -> {v}" for v in expected_ll1_parse_table[str(n)][str(t)]
                ]
                assert len(prods) == len(expected_prods)
                for prod in prods:
                    assert str(prod) in expected_prods
            else:
                assert cfg.ll1_parse_table[n][t] == set()


def test_is_right_recursive():
    A = NonTerminal("A")
    B = NonTerminal("B")
    C = NonTerminal("C")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    def test_productions(productions, expected_value):
        cfg = CFG({A, B, C}, {a, b, c}, productions, A)
        assert cfg.is_right_recursive() == expected_value

    test_productions(
        {
            A: [[a, b, A]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, b, A], [a, A, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
        },
        False,
    )
    test_productions(
        {
            A: [[a, b, A]],
            B: [[a, B, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
            B: [[a, B, b]],
        },
        False,
    )
    test_productions(
        {
            A: [[a, b, A]],
            B: [[a, B, b]],
            C: [[C, a, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
            B: [[a, B, b]],
            C: [[C, a, b]],
        },
        False,
    )


def test_is_left_recursive():
    A = NonTerminal("A")
    B = NonTerminal("B")
    C = NonTerminal("C")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    def test_productions(productions, expected_value):
        cfg = CFG({A, B, C}, {a, b, c}, productions, A)
        assert cfg.is_left_recursive() == expected_value

    test_productions(
        {
            A: [[A, a, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[A, a, b], [a, A, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
        },
        False,
    )
    test_productions(
        {
            A: [[A, a, b]],
            B: [[a, B, b]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
            B: [[a, B, b]],
        },
        False,
    )
    test_productions(
        {
            A: [[A, a, b]],
            B: [[a, B, b]],
            C: [[a, b, C]],
        },
        True,
    )
    test_productions(
        {
            A: [[a, A, b]],
            B: [[a, B, b]],
            C: [[a, b, C]],
        },
        False,
    )


def test_add_starting_production():
    A = NonTerminal("A")
    B = NonTerminal("B")
    C = NonTerminal("C")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    P = {
        A: [[a, b, c]],
        B: [[A], [epsilon]],
    }

    cfg = CFG({A, B, C}, {a, b, c}, P, A, add_unique_starting_production=True)

    S = NonTerminal("S")
    assert cfg.N == {A, B, C, S}
    assert cfg.P[S] == [Production(S, [A])]


def test_lr0_items():
    A = NonTerminal("A")
    B = NonTerminal("B")
    C = NonTerminal("C")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    P = {
        A: [[a, b, c]],
        B: [[A], [epsilon]],
    }

    cfg = CFG({A, B, C}, {a, b, c}, P, A)

    expected_item_strings = [
        "A -> ⋅abc",
        "A -> a⋅bc",
        "A -> ab⋅c",
        "A -> abc⋅",
        "B -> ⋅A",
        "B -> A⋅",
        "B -> ⋅",
    ]

    actual_item_strings = [str(item) for item in cfg.lr0_items]

    for item in expected_item_strings:
        assert item in actual_item_strings
    for item in actual_item_strings:
        assert item in expected_item_strings


def test_lr0_items_with_S():
    A = NonTerminal("A")
    B = NonTerminal("B")
    C = NonTerminal("C")

    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

    P = {
        A: [[a, b, c]],
        B: [[A], [epsilon]],
    }

    cfg = CFG({A, B, C}, {a, b, c}, P, A, add_unique_starting_production=True)

    expected_item_strings = [
        "S -> ⋅A",
        "S -> A⋅",
        "A -> ⋅abc",
        "A -> a⋅bc",
        "A -> ab⋅c",
        "A -> abc⋅",
        "B -> ⋅A",
        "B -> A⋅",
        "B -> ⋅",
    ]

    actual_item_strings = [str(item) for item in cfg.lr0_items]

    for item in expected_item_strings:
        assert item in actual_item_strings
    for item in actual_item_strings:
        assert item in expected_item_strings


def test_lr0_dfa_notes():
    E = NonTerminal("E")
    T = NonTerminal("T")
    F = NonTerminal("F")

    ident = Terminal("id")
    o_bracket = Terminal("(")
    c_bracket = Terminal(")")
    plus = Terminal("+")
    times = Terminal("*")

    P = {
        E: [[E, plus, T], [T]],
        T: [[T, times, F], [F]],
        F: [[ident], [o_bracket, E, c_bracket]],
    }

    cfg = CFG(
        {E, T, F},
        {ident, o_bracket, c_bracket, plus, times},
        P,
        E,
        terminals_order=[o_bracket, ident, c_bracket, plus, times],
        nonterminals_order=[E, T, F],
        add_unique_starting_production=True,
    )

    dfa = cfg.lr0_dfa

    expected_states = [
        frozenset(
            {
                # I0
                "S -> ⋅E",
                "E -> ⋅E+T",
                "E -> ⋅T",
                "T -> ⋅T*F",
                "T -> ⋅F",
                "F -> ⋅ id",
                "F -> ⋅(E)",
            }
        ),
        frozenset(
            {
                # I1
                "S -> E⋅",
                "E -> E⋅+T",
            }
        ),
        frozenset(
            {
                # I2
                "E -> T⋅",
                "T -> T⋅*F",
            }
        ),
        frozenset(
            {
                # I3
                "T -> F⋅",
            }
        ),
        frozenset(
            {
                # I4
                "F -> (⋅E)",
                "E -> ⋅E+T",
                "E -> ⋅T",
                "T -> ⋅T*F",
                "T -> ⋅F",
                "F -> ⋅ id",
                "F -> ⋅(E)",
            }
        ),
        frozenset(
            {
                # I5
                "F -> id ⋅",
            }
        ),
        frozenset(
            {
                # I6
                "E -> E+⋅T",
                "T -> ⋅T*F",
                "T -> ⋅F",
                "F -> ⋅ id",
                "F -> ⋅(E)",
            }
        ),
        frozenset(
            {
                # I7
                "T -> T*⋅F",
                "F -> ⋅ id",
                "F -> ⋅(E)",
            }
        ),
        frozenset(
            {
                # I8
                "F -> (E⋅)",
                "E -> E⋅+T",
            }
        ),
        frozenset(
            {
                # I9
                "E -> E+T⋅",
                "T -> T⋅*F",
            }
        ),
        frozenset(
            {
                # I10
                "T -> T*F⋅",
            }
        ),
        frozenset(
            {
                # I11
                "F -> (E)⋅",
            }
        ),
        frozenset(),  # I12 (Not in the notes)
    ]

    for actual, expected in zip(dfa.state_list, expected_states):
        assert frozenset({str(item) for item in actual}) == expected

    stringified_state_list = [
        frozenset({str(item) for item in state}) for state in dfa.state_list
    ]
    assert stringified_state_list == expected_states

    def index(state):
        return dfa.state_list.index(state)

    def printable_index(state):
        return f"I{index(state):<2}"

    actual_transitions = []
    for q in dfa.state_list:
        for c in dfa.Sigma:
            if (q_prime := dfa.delta(q, c)) != frozenset():
                actual_transitions.append((index(q), c, index(q_prime)))
                print(printable_index(q), c, printable_index(q_prime))

    expected_transitions = [
        (0, E, 1),
        (0, T, 2),
        (0, F, 3),
        (0, o_bracket, 4),
        (0, ident, 5),
        # 1
        (1, plus, 6),
        # 2
        (2, times, 7),
        # 4
        (4, T, 2),
        (4, F, 3),
        (4, o_bracket, 4),
        (4, ident, 5),
        (4, E, 8),
        # 6
        (6, F, 3),
        (6, o_bracket, 4),
        (6, ident, 5),
        (6, T, 9),
        # 7
        (7, o_bracket, 4),
        (7, ident, 5),
        (7, F, 10),
        # 8
        (8, plus, 6),
        (8, c_bracket, 11),
        # 9
        (9, times, 7),
    ]

    for transition in actual_transitions:
        assert transition in expected_transitions
    for transition in expected_transitions:
        assert transition in actual_transitions

    expected_action = [
        {
            # I0
            ident: LR0_Shift(ident, 5),
            o_bracket: LR0_Shift(o_bracket, 4),
        },
        {
            # I1
            plus: LR0_Shift(plus, 6),
            dollar: LR0_Accept(),
        },
        {
            # I2
            plus: LR0_Reduce(Production(E, [T])),
            times: LR0_Shift(times, 7),
            c_bracket: LR0_Reduce(Production(E, [T])),
            dollar: LR0_Reduce(Production(E, [T])),
        },
        {
            # I3
            plus: LR0_Reduce(Production(T, [F])),
            times: LR0_Reduce(Production(T, [F])),
            c_bracket: LR0_Reduce(Production(T, [F])),
            dollar: LR0_Reduce(Production(T, [F])),
        },
        {
            # I4
            ident: LR0_Shift(ident, 5),
            o_bracket: LR0_Shift(o_bracket, 4),
        },
        {
            # I5
            plus: LR0_Reduce(Production(F, [ident])),
            times: LR0_Reduce(Production(F, [ident])),
            c_bracket: LR0_Reduce(Production(F, [ident])),
            dollar: LR0_Reduce(Production(F, [ident])),
        },
        {
            # I6
            ident: LR0_Shift(ident, 5),
            o_bracket: LR0_Shift(o_bracket, 4),
        },
        {
            # I7
            ident: LR0_Shift(ident, 5),
            o_bracket: LR0_Shift(o_bracket, 4),
        },
        {
            # I8
            plus: LR0_Shift(plus, 6),
            c_bracket: LR0_Shift(c_bracket, 11),
        },
        {
            # I9
            plus: LR0_Reduce(Production(E, [E, plus, T])),
            times: LR0_Shift(times, 7),
            c_bracket: LR0_Reduce(Production(E, [E, plus, T])),
            dollar: LR0_Reduce(Production(E, [E, plus, T])),
        },
        {
            # I10
            plus: LR0_Reduce(Production(T, [T, times, F])),
            times: LR0_Reduce(Production(T, [T, times, F])),
            c_bracket: LR0_Reduce(Production(T, [T, times, F])),
            dollar: LR0_Reduce(Production(T, [T, times, F])),
        },
        {
            # I11
            plus: LR0_Reduce(Production(F, [o_bracket, E, c_bracket])),
            times: LR0_Reduce(Production(F, [o_bracket, E, c_bracket])),
            c_bracket: LR0_Reduce(Production(F, [o_bracket, E, c_bracket])),
            dollar: LR0_Reduce(Production(F, [o_bracket, E, c_bracket])),
        },
        set(),  # I12 is failed state, also not in notes
    ]

    expected_goto = [
        {E: 1, T: 2, F: 3},  # I0
        set(),  # I1
        set(),  # I2
        set(),  # I3
        {E: 8, T: 2, F: 3},  # I4
        set(),  # I5
        {T: 9, F: 3},  # I6
        {F: 10},  # I7
        set(),  # I8
        set(),  # I9
        set(),  # I10
        set(),  # I11
        set(),  # I12
        set(),  # I13
    ]

    cfg.print_slr1_action()
    print()
    cfg.print_slr1_goto()
    print()
    print(cfg.slr1_goto)

    for i in range(len(expected_states)):
        for t in cfg.terminals_order + [dollar]:
            if t in expected_action[i]:
                assert cfg.slr1_action[i][t] == [expected_action[i][t]]
            else:
                # Actual table uses the empty list, I ommitted it for clarity above
                assert cfg.slr1_action[i][t] == []

        for n in cfg.nonterminals_order:
            if n in expected_goto[i]:
                assert cfg.slr1_goto[i][n] == expected_goto[i][n]
            else:
                # Actual table uses the None, I ommitted it for clarity above
                assert cfg.slr1_goto[i][n] is None, (i, n)
