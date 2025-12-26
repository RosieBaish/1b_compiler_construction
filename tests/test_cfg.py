from cfg import CFG, epsilon, g3_prime, NonTerminal, Terminal


def test_G3_prime_nullable():
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
    dollar = Terminal("$")

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


def test_G3_prime_parse_table():
    G3_prime = g3_prime()

    expected_values = {
        "S": {"id": ["E$"], "(": ["E$"]},
        "E": {"id": ["TE'"], "(": ["TE'"]},
        "E'": {"+": ["+TE'"], ")": ["ε"], "$": ["ε"]},
        "T": {"id": ["FT'"], "(": ["FT'"]},
        "T'": {"+": ["ε"], "*": ["*FT'"], ")": ["ε"], "$": ["ε"]},
        "F": {"id": ["id"], "(": ["(E)"]},
    }

    G3_prime.print_parse_table()

    for n in G3_prime.N:
        for t in G3_prime.T:
            if str(t) in expected_values[str(n)]:
                prods = G3_prime.parse_table[n][t]
                expected_prods = [
                    f"{n} -> {v}" for v in expected_values[str(n)][str(t)]
                ]
                assert len(prods) == len(expected_prods)
                for prod in prods:
                    assert str(prod) in expected_prods
            else:
                assert G3_prime.parse_table[n][t] == set()


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
        nullable_hints={S: False},
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

    expected_parse_table = {
        "S'": {"a": ["S$"], "b": ["S$"], "c": ["S$"]},
        "S": {"a": ["XYS", "a"], "b": ["XYS"], "c": ["XYS"]},
        "X": {"a": ["Y"], "b": ["Y", "b"], "c": ["Y"]},
        "Y": {"a": ["ε"], "b": ["ε"], "c": ["ε", "c"]},
    }

    cfg.print_parse_table()

    for n in cfg.N:
        for t in cfg.T:
            if str(t) in expected_parse_table[str(n)]:
                prods = cfg.parse_table[n][t]
                expected_prods = [
                    f"{n} -> {v}" for v in expected_parse_table[str(n)][str(t)]
                ]
                assert len(prods) == len(expected_prods)
                for prod in prods:
                    assert str(prod) in expected_prods
            else:
                assert cfg.parse_table[n][t] == set()
