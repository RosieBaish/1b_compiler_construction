from common import (
    Terminal,
    NonTerminal,
    LR0_Action,
    LR0_Shift,
    LR0_Reduce,
    LR0_Accept,
    dollar,
)
from lexer import Lexer


def lex_internal(
    Regexes: list[tuple[Terminal, str, list[str]]], source: str
) -> list[Terminal]:
    # I don't particularly want to be importing the entire Lexer implementation here
    # But it gets it working for now
    lexer = Lexer(Regexes)
    return lexer.lex(source) + [dollar]


class ParseError(Exception):
    def __init__(self, message: str, source_index: int, source: list[Terminal]):
        self.message = message
        self.source_index = source_index
        self.source = source

    def __str__(self) -> str:
        return f"Parse Error {self.message} at index {self.source_index} ({self.source[self.source_index]}). Full text {self.source}"


def parse_internal(
    Action: dict[int, dict[Terminal, list[LR0_Action]]],
    Goto: dict[int, dict[NonTerminal, int]],
    source: list[Terminal],
) -> str:
    parser_stack = [0]
    semantic_stack: list[str] = []
    source_index = 0
    assert len(parser_stack) == len(semantic_stack) + 1, (
        "Error - invalid stack lengths",
        parser_stack,
        semantic_stack,
    )

    while True:
        assert source_index < len(source), (
            "Unexpected EOF, are you missing the dollar?",
            source_index - 1,
            source,
        )
        a = source[source_index]
        s = parser_stack[-1]
        action_list = Action[s][a]
        if len(action_list) == 0:
            raise ParseError(
                "Unexpected token, unable to proceed", source_index, source
            )
        assert len(action_list) == 1, ("Invalid ACTION table", s, a, action_list)
        action = action_list[0]
        if isinstance(action, LR0_Shift):
            assert a == action.t, ("Invalid Shift Action", s, a, action)
            assert action.next_state is not None, ("Invalid Shift Action", s, a, action)
            parser_stack.append(action.next_state)
            semantic_stack.append(str(a))
            assert len(parser_stack) == len(semantic_stack) + 1, (
                "Error - invalid stack lengths",
                parser_stack,
                semantic_stack,
            )
            source_index += 1
        elif isinstance(action, LR0_Reduce):
            assert len(parser_stack) > len(action.prod), (
                "Invalid Reduce Action",
                s,
                a,
                action,
                parser_stack,
            )
            assert len(semantic_stack) >= len(action.prod), (
                "Invalid Reduce Action",
                s,
                a,
                action,
                semantic_stack,
            )
            parser_stack = parser_stack[: -1 * len(action.prod)]
            semantic_elements = semantic_stack[-1 * len(action.prod) :]
            semantic_stack = semantic_stack[: -1 * len(action.prod)]

            parser_stack.append(Goto[parser_stack[-1]][action.prod.LHS])
            semantic_stack.append(f"{action.prod.LHS}({', '.join(semantic_elements)})")
            assert len(parser_stack) == len(semantic_stack) + 1, (
                "Error - invalid stack lengths",
                parser_stack,
                semantic_stack,
            )
        else:
            assert isinstance(action, LR0_Accept), (
                "Invalid ACTION table",
                s,
                a,
                action,
            )
            assert source_index == len(source) - 1, (
                "Unexpected tokens at end of file",
                source_index,
                source,
            )
            assert len(parser_stack) == 2 and parser_stack[0] == 0, (
                "Unexpected tokens on parser_stack",
                parser_stack,
            )
            assert len(semantic_stack) == 1, (
                "Incorrect semantic stack",
                semantic_stack,
            )
            return semantic_stack[0]
