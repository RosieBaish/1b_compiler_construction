from common import NonTerminal, Terminal, LR0_Action, LR0_Shift, LR0_Reduce, LR0_Accept
from grammar_reader import Grammar

from typing import Optional


class ParserGenerator:
    """Generates a parser from {cfg} and puts it in {filename}

    That file will have a class for each NonTerminal of the AST
    That class will have member variables for it's children, plus those specified in {ast_members}
    It will have the functions in {ast_functions}, plus standard ones
    """

    def __init__(
        self,
        g: Grammar,
        filename: str,
        ast_members: list[str],
        ast_functions: list[str],
    ):
        self.g = g
        self.cfg = g.cfg
        self.filename = filename
        self.ast_members = ast_members
        self.ast_functions = ast_functions
        # Squash the dict of lists
        self.production_list = [x for y in self.cfg.P.values() for x in y]

    @staticmethod
    def dict_to_string(d: dict[str, str], indent: int = 0) -> str:
        dict_string: str = "{\n"
        for k, v in d.items():
            dict_string += f"{' ' * (indent + 4)}{k}: {v},\n"
        dict_string += f"{' ' * (indent)}}}"
        return dict_string

    def action_to_string(self) -> str:
        def stringify(a: LR0_Action) -> str:
            if isinstance(a, LR0_Shift):
                return f'LR0_Shift(Terminal("{a.t.name}"), {a.next_state})'
            elif isinstance(a, LR0_Reduce):
                return f"LR0_Reduce(_P[{self.production_list.index(a.prod)}])"
            else:
                assert isinstance(a, LR0_Accept), a
                return "LR0_Accept()"

        stringified_Action: dict[str, dict[str, str]] = {
            str(i): {
                f'Terminal("{t}")': (
                    f"{stringify(action) if action is not None else str(None)}"
                )
                for t, action in row.items()
            }
            for i, row in self.cfg.slr1_action.items()
        }
        stringified_Action_1_level = {
            k: ParserGenerator.dict_to_string(v, indent=4)
            for k, v in stringified_Action.items()
        }
        return (
            "_Action: dict[int, dict[Terminal, Optional[LR0_Action]]] = "
            + ParserGenerator.dict_to_string(stringified_Action_1_level)
            + "\n\n"
        )

    def goto_to_string(self) -> str:
        stringified_Goto: dict[str, dict[str, str]] = {
            str(i): {
                f'NonTerminal("{n}")': str(goto_item) for n, goto_item in row.items()
            }
            for i, row in self.cfg.slr1_goto.items()
        }
        stringified_Goto_1_level = {
            k: ParserGenerator.dict_to_string(v, indent=4)
            for k, v in stringified_Goto.items()
        }
        return (
            "_Goto: dict[int, dict[NonTerminal, Optional[int]]] = "
            + ParserGenerator.dict_to_string(stringified_Goto_1_level)
            + "\n\n"
        )

    def terminals_to_string(self) -> str:
        return (
            "_T: list[Terminal] = [\n"
            + "".join([f'    Terminal("{t.name}"),\n' for t in self.g.terminals])
            + "]\n\n"
        )

    def nonterminals_to_string(self) -> str:
        return (
            "_N: list[NonTerminal] = [\n"
            + "".join([f'    NonTerminal("{n.name}"),\n' for n in self.g.nonterminals])
            + "]\n\n"
        )

    def productions_to_string(self) -> str:
        production_strings: list[str] = []
        for prod in self.production_list:
            rhs = f"_N[{self.g.nonterminals.index(prod.LHS)}]"

            rhs_strings: list[str] = []
            for symbol in prod.RHS:
                if isinstance(symbol, Terminal):
                    rhs_strings.append(f"_T[{self.g.terminals.index(symbol)}]")
                else:
                    assert isinstance(symbol, NonTerminal)
                    rhs_strings.append(f"_N[{self.g.nonterminals.index(symbol)}]")
            if len(rhs_strings) < 8:  # Fairly arbitrary limit
                production_string = f"    Production({rhs}, ["
                production_string += ", ".join(rhs_strings)
                production_string += "]),\n"
            else:
                production_string = "    Production(\n"
                production_string += f"        {rhs},\n"
                production_string += "        [\n"
                # Too long for one line, split it
                rhs_strings = [(" " * 12 + s + ",\n") for s in rhs_strings]
                production_string += "".join(rhs_strings)
                production_string += "        ],\n"
                production_string += "    ),\n"
            production_strings.append(production_string)
        return "_P: list[Production] = [\n" + "".join(production_strings) + "]\n\n"

    def regexes_to_string(self) -> str:
        regex_string_list: list[str] = []
        for t, r, actions in self.g.terminal_triples:
            escaped_r = (
                r.replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t")
            )
            regex_string = f'    (Terminal("{t.name}"), "{escaped_r}", ['
            regex_string += ", ".join(f'"{action}"' for action in actions)
            regex_string += "]),\n"
            regex_string_list.append(regex_string)
        return (
            "_Regexes: list[tuple[Terminal, str, list[str]]] = [\n"
            + "".join(regex_string_list)
            + "]\n\n"
        )

    def generate(
        self,
    ) -> None:  # pragma: no cover, This is tested by testing the generated parsers
        imports: list[tuple[Optional[str], str]] = [
            ("common", "Production"),
            (None, "argparse"),
        ]
        with open(self.filename, "w+", encoding="utf-8") as f:
            for from_name, import_name in imports:
                if from_name is None:
                    f.write(f"import {import_name}\n")
                else:
                    f.write(f"from {from_name} import {import_name}\n")
            with open("parser_stub.py", "r", encoding="utf-8") as parser_stub:
                f.write(parser_stub.read())
            f.write("\n\n")
            f.write(self.terminals_to_string())
            f.write(self.nonterminals_to_string())
            f.write(self.productions_to_string())
            f.write(self.action_to_string())
            f.write(self.goto_to_string())
            f.write(self.regexes_to_string())
            f.write(f"""
def lex(source: str) -> list[Terminal]:
    return lex_internal(_Regexes, source)


_semantic_actions: dict[NonTerminal, Callable[[list[Any]], Any]] = {{
    n: (lambda n: lambda xs: f"{{n}}({{', '.join([str(x) for x in xs])}})")(n) for n in _N
}}


def parse(source: list[Terminal]) -> str:
    return parse_internal(_Action, _Goto, _semantic_actions, source)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="{self.g.name} Parser",
        description="An automatically generated parser for the {self.g.name} language",
    )

    parser.add_argument("filename", nargs="?")
    parser.add_argument("--source", action="store")

    args = parser.parse_args()

    if args.source:
        print(parse(lex(args.source)))
    else:
        if not args.filename:
            parser.print_help()
            exit()
        with open(args.filename, "r", encoding="utf-8") as f:
            print(parse(lex(f.read())))


if __name__ == "__main__":
    main()
""")


def main() -> None:
    g = Grammar.from_file("g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "generated_g2_parser.py", [], [])
    pg.generate()

    g = Grammar.from_file("slang.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "generated_slang_parser.py", [], [])
    pg.generate()
