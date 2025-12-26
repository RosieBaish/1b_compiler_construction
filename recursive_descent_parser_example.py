from string import ascii_lowercase
from typing import Optional

"""A recursive descent parser for the example on page 28(53) of Lecture 3 of the notes.
Parses strings containing single letter lowercase variables plus +*() which are valid maths"""


class E:
    def __init__(self, t: "T", e_prime: "E_prime"):
        self.t = t
        self.e_prime = e_prime

    @staticmethod
    def parse(s: str) -> tuple["E", str]:
        t, cont1 = T.parse(s)
        e_prime, cont2 = E_prime.parse(cont1)
        return (E(t, e_prime), cont2)

    def __str__(self) -> str:
        return f"E({self.t}, {self.e_prime})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, E) and self.t == other.t and self.e_prime == other.e_prime
        )


class E_prime:
    def __init__(self, t: Optional["T"], e_prime: Optional["E_prime"]):
        assert (t is None) == (e_prime is None), (t, e_prime)

        self.is_epsilon = t is None and e_prime is None
        self.t = t
        self.e_prime = e_prime

    @staticmethod
    def parse(s: str) -> tuple["E_prime", str]:
        if len(s) and s[0] == "+":
            t, cont1 = T.parse(s[1:])
            e_prime, cont2 = E_prime.parse(cont1)
            return (E_prime(t, e_prime), cont2)
        else:
            return (E_prime(None, None), s)

    def __str__(self) -> str:
        return "E_prime()" if self.is_epsilon else f"E_prime({self.t}, {self.e_prime})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, E_prime)
            and self.t == other.t
            and self.e_prime == other.e_prime
        )


class T:
    def __init__(self, f: "F", t_prime: "T_prime"):
        self.f = f
        self.t_prime = t_prime

    @staticmethod
    def parse(s: str) -> tuple["T", str]:
        f, cont1 = F.parse(s)
        t_prime, cont2 = T_prime.parse(cont1)
        return (T(f, t_prime), cont2)

    def __str__(self) -> str:
        return f"T({self.f}, {self.t_prime})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, T) and self.f == other.f and self.t_prime == other.t_prime
        )


class T_prime:
    def __init__(self, f: Optional["F"], t_prime: Optional["T_prime"]):
        assert (f is None) == (t_prime is None), (f, t_prime)

        self.is_epsilon = f is None and t_prime is None
        self.f = f
        self.t_prime = t_prime

    @staticmethod
    def parse(s: str) -> tuple["T_prime", str]:
        if len(s) and s[0] == "*":
            f, cont1 = F.parse(s[1:])
            t_prime, cont2 = T_prime.parse(cont1)
            return (T_prime(f, t_prime), cont2)
        else:
            return (T_prime(None, None), s)

    def __str__(self) -> str:
        return "T_prime()" if self.is_epsilon else f"T_prime({self.f}, {self.t_prime})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, T_prime)
            and self.f == other.f
            and self.t_prime == other.t_prime
        )


class F:
    def __init__(self, e: Optional["E"], token: Optional[str]):
        assert (e is None) ^ (token is None), (e, token)
        self.is_id = token is not None
        self.e = e
        self.token = token

    @staticmethod
    def parse(s: str) -> tuple["F", str]:
        if len(s) and s[0] == "(":
            e, cont1 = E.parse(s[1:])
            assert cont1[0] == ")"
            cont2 = cont1[1:]
            return (F(e, None), cont2)
        elif len(s) and s[0] in ascii_lowercase:
            cont = s[1:]
            return (F(None, s[0]), cont)
        else:
            assert False, ("Unexpected token while parsing F", s)

    def __str__(self) -> str:
        return f"F({self.token})" if self.is_id else f"F({self.e})"

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, F) and self.e == other.e and self.token == other.token


def main() -> None:
    print(E.parse("x+y*z"))
