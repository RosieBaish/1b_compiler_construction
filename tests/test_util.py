import util


def test_set_to_range_string():
    assert util.set_to_range_string({}) == "[]"
    assert util.set_to_range_string({""}) == "[ε]"
    assert util.set_to_range_string({"0"}) == "[0]"
    assert util.set_to_range_string({"0", "1"}) == "[01]"
    assert util.set_to_range_string({"0", "1", "2"}) == "[0-2]"
    assert util.set_to_range_string({"0", "1", "2", "4"}) == "[0-24]"
    assert util.set_to_range_string({"0", "1", "2", "4", "5"}) == "[0-245]"
    assert util.set_to_range_string({"0", "1", "2", "4", "5", ""}) == "[ε0-245]"
    assert util.set_to_range_string({"0", "1", "2", "4", "5", "", "a"}) == "[ε0-245a]"
    assert (
        util.set_to_range_string({"0", "1", "2", "4", "5", "", "a", "b"})
        == "[ε0-245ab]"
    )
    assert (
        util.set_to_range_string({"0", "1", "2", "4", "5", "", "a", "b", "c"})
        == "[ε0-245a-c]"
    )


def test_range_string_to_set():
    assert set() == util.range_string_to_set("[]")
    assert {""} == util.range_string_to_set("[ε]")
    assert {"0"} == util.range_string_to_set("[0]")
    assert {"0", "1"} == util.range_string_to_set("[01]")
    assert {"0", "1", "2"} == util.range_string_to_set("[0-2]")
    assert {"0", "1", "2", "4"} == util.range_string_to_set("[0-24]")
    assert {"0", "1", "2", "4", "5"} == util.range_string_to_set("[0-245]")
    assert {"0", "1", "2", "4", "5", ""} == util.range_string_to_set("[ε0-245]")
    assert {"0", "1", "2", "4", "5", "", "a"} == util.range_string_to_set("[ε0-245a]")
    assert {"0", "1", "2", "4", "5", "", "a", "b"} == util.range_string_to_set(
        "[ε0-245ab]"
    )
    assert {"0", "1", "2", "4", "5", "", "a", "b", "c"} == util.range_string_to_set(
        "[ε0-245a-c]"
    )
