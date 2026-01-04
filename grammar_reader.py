from cfg import CFG
from common import Terminal, NonTerminal, Symbol, epsilon
from regex import Regex

from typing import Optional

"""Methods to allow writing grammars in a slightly better format than them being python datastructures
i.e. We want "A -> a A B" rather than "{A: [[a, A, B]]}"

Given that it's new-line based, you can't have literal new line characters (ascii 10) in regexes, so you use \n
(ascii 92, ascii 110). This needs to be replaced with literal new line (ascii 10) before passing to the regex engine.
Ditto tabs. You can have tabs without breaking the parser, but enough IDEs break tabs in weird ways
that it seems sensible to support \t

File Format is below, you can put whitespace only lines anywhere you like:
'Grammar: {name}'

'Terminals Start'
'{TokenName}}: "{regex}"' [STORE | IGNORE] (store the value of the token, or ignore it post lexing)
'Terminals End'

'NonTerminals Start'
'{NonTerminal Name}'
'NonTerminals End'

'Productions Start'
'{NonTerminal} -> {Symbol} {Symbol} [...]
'{whitespace}   | {Symbol} {Symbol} [...]' (Optional, reuses previous nonterminal)
'Productions End'

Start Symbol: {NonTerminal}

"""


class Grammar:
    def __init__(
        self,
        *,
        filename: str = "",
        contents: str = "",
        add_starting_production: bool = False,
    ):
        # I'm deliberately not parsing this 'properly' because we're implementing a parser here
        # And so I'm avoiding the built-in stuff.
        # Ditto regexes etc.

        assert (filename == "") ^ (contents == "")

        self.add_starting_production = add_starting_production

        self.name: str
        self.terminal_triples: list[tuple[Terminal, Regex, list[str]]] = []
        self.nonterminals: list[NonTerminal] = []
        self.productions: dict[NonTerminal, list[list[Symbol]]] = {}
        self.start_symbol: NonTerminal

        self._cfg: Optional[CFG] = None

        if filename != "":
            with open(filename) as f:
                lines = f.readlines()
        else:
            lines = contents.split("\n")

        lines = [line.strip() for line in lines if line.strip() != ""]

        grammar_colon = "Grammar: "
        assert lines[0].startswith(grammar_colon)
        self.name = lines[0][len(grammar_colon) :]

        assert lines[1] == "Terminals Start"
        line_num = 2
        terminals_end = "Terminals End"
        while lines[line_num] != terminals_end:
            # Should be of the form {token name}: "{regex}" STORE
            # Where the STORE is optional

            terminal_name, _, rest = lines[line_num].partition(":")

            potential_actions = ["STORE", "IGNORE"]  # Mutually Exclusive
            actions = []
            for action in potential_actions:
                if rest.endswith(action):
                    actions.append(action)
                    rest = rest[: -1 * len(action)]

            rest = rest.strip()

            assert len(rest) >= 2 and rest[0] == '"' and rest[-1] == '"', (
                rest,
                lines[line_num],
            )

            rest = rest[1:-1]  # Remove quotes

            backslash = chr(92)  # Using the ascii code here to be unambiguous

            rest = rest.replace(backslash + "n", "\n")
            rest = rest.replace(backslash + "t", "\t")

            regex = Regex.parse(rest)

            self.terminal_triples.append((Terminal(terminal_name), regex, actions))
            line_num += 1
        assert lines[line_num] == terminals_end
        line_num += 1

        assert lines[line_num] == "NonTerminals Start"
        line_num += 1
        nonterminals_end = "NonTerminals End"
        while lines[line_num] != nonterminals_end:
            # Can't have a terminal and nonterminal with the same name
            assert Terminal(lines[line_num]) not in self.terminals, lines[line_num]
            self.nonterminals.append(NonTerminal(lines[line_num]))
            line_num += 1
        assert lines[line_num] == nonterminals_end
        line_num += 1

        def parse_symbol_list(symbols: str) -> list[Symbol]:
            symbols = symbols.strip()
            if symbols == "epsilon":
                return [epsilon]

            symbol_list: list[Symbol] = []
            for symbol in symbols.split():
                if (nt := NonTerminal(symbol)) in self.nonterminals:
                    symbol_list.append(nt)
                elif (t := Terminal(symbol)) in self.terminals:
                    symbol_list.append(t)
                else:
                    found = False
                    for t, r, _ in self.terminal_triples:
                        if r.test_string(symbol):
                            symbol_list.append(t)
                            found = True
                            break
                    assert found, symbol
            return symbol_list

        assert lines[line_num] == "Productions Start"
        line_num += 1
        productions_end = "Productions End"
        prev_nonterminal: Optional[NonTerminal] = None
        while lines[line_num] != productions_end:
            # A production is either "{NonTerminal} -> {Symbol}+"
            # Or "| {Symbol}+"
            # Note that "epsilon" is a valid RHS as well

            if lines[line_num].startswith("|"):
                assert prev_nonterminal is not None
                rhs = lines[line_num][1:].strip()
                self.productions[prev_nonterminal].append(parse_symbol_list(rhs))
            else:
                assert "->" in lines[line_num], lines[line_num]
                _nonterminal, _, rhs = lines[line_num].partition("->")
                nonterminal = NonTerminal(_nonterminal.strip())

                if nonterminal not in self.productions:
                    self.productions[nonterminal] = []

                self.productions[nonterminal].append(parse_symbol_list(rhs.strip()))

                prev_nonterminal = nonterminal

            line_num += 1
        assert lines[line_num] == productions_end
        line_num += 1

        start_symbol = "Start Symbol: "
        assert lines[line_num].startswith(start_symbol)
        self.start_symbol = NonTerminal(lines[line_num][len(start_symbol) :])
        assert self.start_symbol in self.nonterminals, (
            self.start_symbol,
            self.nonterminals,
        )

    @property
    def terminals(self) -> list[Terminal]:
        return [t for (t, _, _) in self.terminal_triples]

    @property
    def cfg(self) -> CFG:
        if self._cfg is not None:
            return self._cfg
        self._cfg = CFG(
            set(self.nonterminals),
            set(self.terminals),
            self.productions,
            self.start_symbol,
            terminals_order=self.terminals,
            nonterminals_order=self.nonterminals,
            add_unique_starting_production=self.add_starting_production,
        )
        return self._cfg
