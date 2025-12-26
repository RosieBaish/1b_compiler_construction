from cfg import epsilon, g3_prime, Terminal


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
