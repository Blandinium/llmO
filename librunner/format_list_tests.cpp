#include "format_list_tests.h"

#include <cstring>
#include <iostream>
#include <limits>
#include <string>
#include <string_view>

namespace {

bool expect_format_list_equal(
    FormatListFunction format_list,
    FreeStringFunction free_string,
    const int* input,
    std::size_t input_length,
    std::string_view expected,
    const char* case_name
) {
    char* actual = format_list(input, input_length);
    if (actual == nullptr) {
        std::cerr << "format_list " << case_name << " failed: returned nullptr\n";
        return false;
    }

    const std::string_view actual_view(actual, std::strlen(actual));
    const bool matches = actual_view == expected;
    if (!matches) {
        std::cerr << "format_list " << case_name << " failed: expected \""
                  << expected << "\", got \"" << actual_view << "\"\n";
    }

    free_string(actual);
    return matches;
}

} // namespace

bool run_format_list_tests(
    FormatListFunction format_list,
    FreeStringFunction free_string
) {
    if (format_list == nullptr) {
        std::cerr << "format_list function pointer is null\n";
        return false;
    }
    if (free_string == nullptr) {
        std::cerr << "free_string function pointer is null\n";
        return false;
    }

    bool passed = true;

    passed = expect_format_list_equal(
        format_list,
        free_string,
        nullptr,
        0,
        "[]",
        "empty null input"
    ) && passed;

    const int single[] = {42};
    passed = expect_format_list_equal(
        format_list,
        free_string,
        single,
        1,
        "[42]",
        "single value"
    ) && passed;

    const int mixed[] = {-7, 0, 13, 13, 2048};
    passed = expect_format_list_equal(
        format_list,
        free_string,
        mixed,
        5,
        "[-7, 0, 13, 13, 2048]",
        "mixed values"
    ) && passed;

    const int extremes[] = {
        std::numeric_limits<int>::min(),
        std::numeric_limits<int>::max()
    };
    const std::string expected_extremes =
        "[" + std::to_string(std::numeric_limits<int>::min()) + ", " +
        std::to_string(std::numeric_limits<int>::max()) + "]";
    passed = expect_format_list_equal(
        format_list,
        free_string,
        extremes,
        2,
        expected_extremes,
        "integer extremes"
    ) && passed;

    char* invalid = format_list(nullptr, 1);
    if (invalid != nullptr) {
        std::cerr << "format_list invalid null input failed: expected nullptr, got \""
                  << invalid << "\"\n";
        free_string(invalid);
        passed = false;
    }

    return passed;
}
