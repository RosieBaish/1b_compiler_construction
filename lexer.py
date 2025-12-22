from dfa import DFA
from nfa import NFA
from regex import Regex

from string import printable


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
    def __init__(self, token_descriptions: list[tuple[str, str]]):
        nfas = [
            NFA.from_regex(Regex.parse(r), set(printable), accept_tag=t)
            for (r, t) in token_descriptions
        ]
        self.dfa = DFA.fromNFA(NFA.merge_nfas(nfas))

    def lex(self, input_string: str) -> list[tuple[str, str]]:
        characters_consumed = 0
        tokens: list[tuple[str, str]] = []
        while characters_consumed < len(input_string):
            self.dfa.test_string(input_string[characters_consumed:])
            if self.dfa.num_chars_accepted == 0 or self.dfa.last_accept_tag is None:
                raise LexerError(
                    f"Lexing error after {characters_consumed} characters, next character is {input_string[characters_consumed]}",
                    characters_consumed,
                    input_string,
                )
            token = self.dfa.last_accept_tag
            tokens.append(
                (
                    token,
                    input_string[
                        characters_consumed : characters_consumed
                        + self.dfa.num_chars_accepted
                    ],
                )
            )
            characters_consumed += self.dfa.num_chars_accepted
        return tokens


def main() -> None:
    lexer = Lexer(
        [
            ("if", "IF"),
            ("then", "THEN"),
            ("[a-zA-Z]([a-zA-Z0-9])*", "IDENT"),
            ("[0-9]", "INT"),
            ("[ \t\n]", "SKIP"),
        ]
    )
    print(lexer.lex("if x then y"))
