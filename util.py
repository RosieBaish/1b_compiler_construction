def set_to_range_string(input_set: set[str]) -> str:
    for char in input_set:
        assert len(char) in {0, 1}, char
    # Work with ascii/unicode values not characters for simplicity
    ascii_vals = sorted([ord(c) if c != "" else -1 for c in input_set])

    def my_chr(c: int) -> str:
        """Identical to chr but uses -1 for epsilon"""
        if c == -1:
            return "ε"
        else:
            return chr(c)

    if len(ascii_vals) == 0:
        return "[]"
    elif len(ascii_vals) == 1:
        return f"[{my_chr(ascii_vals[0])}]"
    groups: list[str] = []
    current_group: list[int] = [ascii_vals[0]]

    def add_current_group(current_group: list[int]) -> None:
        if len(current_group) < 3:
            groups.extend([my_chr(c) for c in current_group])
        else:
            groups.append(f"{my_chr(current_group[0])}-{my_chr(current_group[-1])}")

    for c in ascii_vals[1:]:
        if c - current_group[-1] == 1:
            # Still contiguous
            current_group.append(c)
        else:
            add_current_group(current_group)
            current_group = [c]
    add_current_group(current_group)

    return "[" + "".join(groups) + "]"


def range_string_to_set(range_string: str) -> set[str]:
    """Range string is of the form [{a}-{b}...{a}-{b}] where {a} and {b} are characters
    It could also have an ε somewhere in there"""
    assert range_string[0] == "["
    assert range_string[-1] == "]"
    output_set: set[str] = set()

    range_string = range_string[1:-1]

    i = 0
    while i + 3 <= len(range_string):
        start = range_string[i]
        if range_string[i + 1] != "-":
            # Handle random loose characters
            if start == "ε":
                output_set |= {""}
            else:
                output_set |= {start}
            i += 1
            continue

        # Handle triples
        assert range_string[i + 1] == "-", (range_string, i)
        end = range_string[i + 2]
        assert ord(end) > ord(start), (start, end, "Ranges must be forwards")
        for c in range(ord(start), ord(end) + 1):
            output_set |= {chr(c)}
        i += 3
    while i < len(range_string):
        start = range_string[i]
        assert start != "-", (range_string, i)
        if start == "ε":
            output_set |= {""}
        else:
            output_set |= {start}
        i += 1
    return output_set
