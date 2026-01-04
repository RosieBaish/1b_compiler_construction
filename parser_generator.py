from common import NonTerminal, Terminal, LR0_Action
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
    ):  # pragma: no cover, This is tested by testing the generated parsers
        self.g = g
        self.cfg = g.cfg
        self.filename = filename
        self.ast_members = ast_members
        self.ast_functions = ast_functions

    @staticmethod
    def dict_to_string(d: dict[str, str], indent: int = 0) -> str:
        dict_string: str = "{\n"
        for k, v in d.items():
            dict_string += f"{' ' * (indent + 4)}{k}: {v},\n"
        dict_string += f"{' ' * (indent)}}}"
        return dict_string

    @staticmethod
    def action_to_string(
        Action: dict[int, dict[Terminal, list[LR0_Action]]], indent: int = 0
    ) -> str:
        stringified_Action: dict[str, dict[str, str]] = {
            str(i): {
                f'Terminal("{t}")': (
                    f"[{', '.join(action.parseable_string() for action in action_list)}]"
                )
                for t, action_list in row.items()
            }
            for i, row in Action.items()
        }
        stringified_Action_1_level = {
            k: ParserGenerator.dict_to_string(v, indent=indent + 4)
            for k, v in stringified_Action.items()
        }
        return (
            "Action = "
            + ParserGenerator.dict_to_string(stringified_Action_1_level, indent=indent)
            + "\n\n"
        )

    @staticmethod
    def goto_to_string(
        Goto: dict[int, dict[NonTerminal, Optional[int]]], indent: int = 0
    ) -> str:
        stringified_Goto: dict[str, dict[str, str]] = {
            str(i): {f'Terminal("{t}")': str(goto_item) for t, goto_item in row.items()}
            for i, row in Goto.items()
        }
        stringified_Goto_1_level = {
            k: ParserGenerator.dict_to_string(v, indent=indent + 4)
            for k, v in stringified_Goto.items()
        }
        return (
            "Goto = "
            + ParserGenerator.dict_to_string(stringified_Goto_1_level, indent=indent)
            + "\n\n"
        )

    def generate(
        self,
    ) -> None:  # pragma: no cover, This is tested by testing the generated parsers
        imports: list[tuple[Optional[str], str]] = [
            ("cfg", "Production"),
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
            f.write(ParserGenerator.action_to_string(self.cfg.slr1_action))
            f.write(ParserGenerator.goto_to_string(self.cfg.slr1_goto))
            f.write("""

def parse(source: list[Terminal]) -> str:
    return parse_internal(Action, Goto, source)
""")


def main() -> None:
    g = Grammar(filename="g2.grammar", add_starting_production=True)
    pg = ParserGenerator(g, "generated_g2_parser.py", [], [])

    pg.generate()
