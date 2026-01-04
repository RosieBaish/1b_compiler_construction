from dfa import DFA
from nfa import TypedNFA
from regex import Regex
from common import Terminal

from string import printable
from typing import Union


class LexerError(BaseException):
    def __init__(self, message: str, characters_consumed: int, input_string: str):
        self.message = message
        self.characters_consumed = characters_consumed
        self.input_string = input_string

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return str((self.message, self.characters_consumed, self.input_string))


class Lexer:
    def __init__(
        self, token_descriptions: list[tuple[Terminal, Union[str | Regex], list[str]]]
    ):
        self.token_descriptions = token_descriptions
        nfas = [
            TypedNFA[str, str, Terminal].from_regex(
                r if isinstance(r, Regex) else Regex.parse(r),
                set(printable),
                accept_tag=t,  # type: ignore # For some reason it can't figure this specific line out
            )
            for (t, r, _) in token_descriptions
        ]
        self.dfa: DFA[str, str, Terminal] = DFA.fromNFA(TypedNFA.merge_nfas(nfas))

    def lex(self, input_string: str) -> list[Terminal]:
        characters_consumed = 0
        tokens: list[Terminal] = []
        while characters_consumed < len(input_string):
            self.dfa.test_string(input_string[characters_consumed:])
            if self.dfa.num_chars_accepted == 0 or self.dfa.last_accept_tag is None:
                raise LexerError(
                    f"Lexing error after {characters_consumed} characters, next character is {input_string[characters_consumed]}",
                    characters_consumed,
                    input_string,
                )
            token = self.dfa.last_accept_tag

            token_actions = next(
                td[2] for td in self.token_descriptions if td[0] == token
            )
            if "IGNORE" not in token_actions:
                if "STORE" in token_actions:
                    tokens.append(
                        Terminal(
                            token.name,
                            input_string[
                                characters_consumed : (
                                    characters_consumed + self.dfa.num_chars_accepted
                                )
                            ],
                        )
                    )
                else:
                    tokens.append(Terminal(token.name))
            characters_consumed += self.dfa.num_chars_accepted

        return tokens


def main() -> None:
    lexer = Lexer(
        [
            (Terminal("IF"), "if", []),
            (Terminal("THEN"), "then", []),
            (Terminal("IDENT"), "[a-zA-Z]([a-zA-Z0-9])*", ["STORE"]),
            (Terminal("INT"), "[0-9]", ["STORE"]),
            (Terminal("SKIP"), "[ \t\n]", ["IGNORE"]),
        ]
    )
    print(lexer.lex("if x then y"))
