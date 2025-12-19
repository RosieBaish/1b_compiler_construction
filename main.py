import argparse

import nfa
import regex


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="1b Compiler Construction",
        description="A selection of code to implement 1b Compiler Construction",
    )

    parser.add_argument("--nfa", action="store_true")
    parser.add_argument("--regex", action="store_true")

    args = parser.parse_args()

    if args.nfa:
        nfa.main()
    if args.regex:
        regex.main()


if __name__ == "__main__":
    main()
