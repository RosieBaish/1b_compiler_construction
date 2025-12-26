from cfg_parser import Parser
from cfg import g3_prime, Terminal


"""
No great way to test this as the parser doesn't produce a parse tree.
So just check the Predict/Consume lines in stdout
"""


def test_g3_prime_output(capfd):
    p = Parser(g3_prime())

    x = Terminal("id", "x")
    y = Terminal("id", "y")
    plus = Terminal("+")
    o_bracket = Terminal("(")
    c_bracket = Terminal(")")

    p.parse([o_bracket, x, plus, y, c_bracket])

    out, _ = capfd.readouterr()
    lines = out.strip().split("\n")

    expected_output = """
Predict E$
Predict TE'
Predict FT'
Predict (E)
Consume (
Predict TE'
Predict FT'
Predict id
Consume id(x)
Predict ε
Predict +TE'
Consume +
Predict FT'
Predict id
Consume id(y)
Predict ε
Predict ε
Consume )
Predict ε
Predict ε
    """.strip().split("\n")

    assert lines == expected_output
