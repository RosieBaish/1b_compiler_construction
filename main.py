import argparse

import cfg
import dfa
import lexer
import nfa
import recursive_descent_parser_example
import regex


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="1b Compiler Construction",
        description="A selection of code to implement 1b Compiler Construction",
    )

    parser.add_argument("--nfa", action="store_true")
    parser.add_argument("--regex", action="store_true")
    parser.add_argument("--dfa", action="store_true")
    parser.add_argument("--lexer", action="store_true")
    parser.add_argument("--recursive-descent-parser-example", action="store_true")
    parser.add_argument("--cfg", action="store_true")

    args = parser.parse_args()

    if args.nfa:
        nfa.main()
    if args.regex:
        regex.main()
    if args.dfa:
        dfa.main()
    if args.lexer:
        lexer.main()
    if args.recursive_descent_parser_example:
        recursive_descent_parser_example.main()
    if args.cfg:
        cfg.main()


if __name__ == "__main__":
    main()
