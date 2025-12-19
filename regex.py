class Regex:
    def test_string(self, string: str) -> bool:
        assert False, "Need to override"

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def parse(regex_string: str) -> "Regex":
        """To make parsing simple, or and star need to be bracketed
        So our language is:
        r := ''
           | a \\in Sigma
           | (r + r) # Using + for OR
           | rr
           | (r)*
        """

        # I'm deliberately not doing this 'properly' because a proper
        # implementation is the end goal

        # Base cases
        if len(regex_string) == 0:
            return EpsilonRegex()
        elif len(regex_string) == 1:
            return CharacterRegex(regex_string)

        continuation = ""
        first_part: "Regex"
        if regex_string[0] == "(":
            # Either Or or Star
            # To figure out which, traverse through and see if we find \/
            # not enclosed in brackets
            bracket_level = 0
            found_or = False
            or_position = -1
            close_bracket_position = -1
            for i, char in enumerate(regex_string[1:], start=1):
                print(i, char)
                if char == "(":
                    bracket_level += 1
                    continue
                elif char == ")":
                    bracket_level -= 1

                    # If it's <0 then we've found more closes than opens
                    # Which means we've close the bracket we started with
                    # So we're done
                    if bracket_level < 0:
                        close_bracket_position = i
                        break
                elif char == "+" and bracket_level == 0:
                    assert not found_or, "Can't have 2 ors in 1 bracket"
                    found_or = True
                    or_position = i
                else:
                    pass

            assert close_bracket_position > 0, (
                regex_string,
                close_bracket_position,
                bracket_level,
            )

            if found_or:
                lhs = regex_string[1:or_position]
                rhs = regex_string[or_position + 1 : close_bracket_position]
                continuation = regex_string[close_bracket_position + 1 :]

                print("OR: ", regex_string, lhs, rhs, continuation)
                first_part = OrRegex(Regex.parse(lhs), Regex.parse(rhs))
            else:
                bracketed_string = regex_string[1:close_bracket_position]
                assert regex_string[close_bracket_position + 1] == "*", (
                    "A non-or bracket has to be a Star"
                )
                continuation = regex_string[close_bracket_position + 2 :]

                print("STAR:", regex_string, bracketed_string, continuation)

                first_part = StarRegex(Regex.parse(bracketed_string))
        else:
            first_part = Regex.parse(regex_string[0])
            continuation = regex_string[1:]

        if len(continuation) == 0:
            return first_part
        else:
            print("Continuation: ", continuation)
            return ConcatenationRegex(first_part, Regex.parse(continuation))


class EmptyRegex(Regex):
    def __str__(self) -> str:
        return "EmptyRegex"

    def test_string(self, _: str) -> bool:
        return False


class EpsilonRegex(Regex):
    def __str__(self) -> str:
        return "EpsilonRegex"

    def test_string(self, string: str) -> bool:
        return string == ""


class CharacterRegex(Regex):
    def __init__(self, character: str):
        self.character = character
        assert len(self.character) == 1, self.character

    def __str__(self) -> str:
        return f"CharacterRegex({self.character})"

    def test_string(self, string: str) -> bool:
        return string == self.character


class OrRegex(Regex):
    def __init__(self, r1: Regex, r2: Regex):
        self.r1 = r1
        self.r2 = r2

    def __str__(self) -> str:
        return f"OrRegex({self.r1}, {self.r2})"

    def test_string(self, string: str) -> bool:
        return self.r1.test_string(string) or self.r2.test_string(string)


class ConcatenationRegex(Regex):
    def __init__(self, r1: Regex, r2: Regex):
        self.r1 = r1
        self.r2 = r2

    def __str__(self) -> str:
        return f"ConcatenationRegex({self.r1}, {self.r2})"

    def test_string(self, string: str) -> bool:
        for i in range(len(string)):
            w1 = string[:i]
            w2 = string[i:]
            print(f'Testing "{w1}" and "{w2}"')

            if self.r1.test_string(w1) and self.r2.test_string(w2):
                return True
        return False


class StarRegex(Regex):
    def __init__(self, r: Regex):
        self.r = r

    def __str__(self) -> str:
        return f"StarRegex({self.r})"

    def test_string(self, string: str) -> bool:
        continuation = string
        print(f'Continuation "{continuation}" (length {len(continuation)})')
        while len(continuation):
            for i in range(len(continuation)):
                if self.r.test_string(continuation[: i + 1]):
                    continuation = continuation[i + 1 :]
                    print(f'Continuation "{continuation}" (length {len(continuation)})')
                    break
                # If we get here we didn't find a substring at
                # the start of continuation that matched
                return False
        # Continuation is now empty so we consumed it all, so string matched.
        return True


def main() -> None:
    r = Regex.parse("a")
    r.test_string("aaa")
