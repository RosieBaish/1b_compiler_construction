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
