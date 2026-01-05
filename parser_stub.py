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

from typing import Any, Callable, Optional


def lex_internal(
    Regexes: list[tuple[Terminal, str, list[str]]], source: str
) -> list[Terminal]:
    # I don't particularly want to be importing the entire Lexer implementation here
    # But it gets it working for now
    lexer = Lexer(Regexes)
    return lexer.lex(source) + [dollar]


class ParseError(Exception):
    def __init__(
        self,
        message: str,
        source_index: int,
        source: list[Terminal],
        valid_terminals: list[Terminal],
    ):
        self.message = message
        self.source_index = source_index
        self.source = source
        self.valid_terminals = valid_terminals

    def __str__(self) -> str:
        return f"""Parse Error {self.message} at index {self.source_index} ({self.source[self.source_index]}).
        Expected one of {[str(t) for t in self.valid_terminals]}
        Full text: {self.source}"""


def parse_internal(
    Action: dict[int, dict[Terminal, Optional[LR0_Action]]],
    Goto: dict[int, dict[NonTerminal, int]],
    semantic_actions: dict[NonTerminal, Callable[[list[Any]], Any]],
    source: list[Terminal],
) -> str:
    def valid_terminals(state: int) -> list[Terminal]:
        return [t for t, a in Action[state].items() if a is not None]

    parser_stack = [0]
    semantic_stack: list[Any] = []
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
        action = Action[s][a]
        if action is None:
            raise ParseError(
                "Unexpected token, unable to proceed",
                source_index,
                source,
                valid_terminals(s),
            )
        if isinstance(action, LR0_Shift):
            assert a == action.t, ("Invalid Shift Action", s, a, action)
            assert action.next_state is not None, ("Invalid Shift Action", s, a, action)
            parser_stack.append(action.next_state)
            semantic_stack.append(a)
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
            semantic_stack.append(semantic_actions[action.prod.LHS](semantic_elements))
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
