from cfg import CFG, g3_prime
from common import Symbol, NonTerminal, Terminal, dollar, epsilon


class Parser:
    def __init__(self, cfg: CFG):
        self.cfg = cfg
        self.stack: list[Symbol] = [cfg.E]

    def parse(self, tokens: list[Terminal]) -> None:
        offset = 0
        tokens.append(dollar)
        while (X := self.stack.pop()) != dollar:
            a = tokens[offset]
            if X == a:
                print(f"Consume {a}")
                offset += 1
            else:
                assert isinstance(X, NonTerminal)
                productions = list(self.cfg.ll1_parse_table[X][a])
                assert len(productions) != 0, ("Parse Error - no rule", tokens, offset)
                assert len(productions) == 1, (
                    "Parse Error - ambuguous situation",
                    tokens,
                    offset,
                    productions,
                )
                production = productions[0]
                print(f"Predict {''.join(str(s) for s in production.RHS)}")
                for s in production.RHS[::-1]:
                    if s != epsilon:
                        self.stack.append(s)


def main() -> None:
    p = Parser(g3_prime())

    x = Terminal("id", "x")
    y = Terminal("id", "y")
    plus = Terminal("+")
    o_bracket = Terminal("(")
    c_bracket = Terminal(")")

    p.parse([o_bracket, x, plus, y, c_bracket])
