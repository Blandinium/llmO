#include "repeated_sort_tests.h"

#include <algorithm>
#include <array>
#include <iostream>
#include <limits>
#include <vector>

namespace {

std::int64_t oracle_repeated_sort(
    const int* input,
    std::size_t input_length,
    int rounds
) {
    if (input == nullptr && input_length != 0) {
        return 0;
    }
    if (input_length == 0) {
        return 0;
    }

    std::vector<int> values(input, input + input_length);
    std::ranges::sort(values);

    const std::size_t mid = values.size() / 2;
    const int median = values.size() % 2 == 0
        ? static_cast<int>(
            (static_cast<std::int64_t>(values[mid - 1]) + values[mid]) / 2
        )
        : values[mid];

    std::int64_t total = 0;
    for (int r = 0; r < rounds; ++r) {
        total += median;
        total += values[static_cast<std::size_t>(r) % values.size()];
    }

    return total;
}

bool expect_equal(
    std::int64_t actual,
    std::int64_t expected,
    const char* case_name
) {
    if (actual == expected) {
        return true;
    }

    std::cerr << "repeated_sort " << case_name << " failed: expected "
              << expected << ", got " << actual << '\n';
    return false;
}

bool expect_case(
    RepeatedSortFunction repeated_sort,
    const int* input,
    std::size_t input_length,
    int rounds,
    const char* case_name
) {
    return expect_equal(
        repeated_sort(input, input_length, rounds),
        oracle_repeated_sort(input, input_length, rounds),
        case_name
    );
}

bool test_edge_cases(RepeatedSortFunction repeated_sort) {
    bool passed = true;

    passed = expect_equal(
        repeated_sort(nullptr, 4, 3),
        0,
        "null input with non-zero length"
    ) && passed;
    passed = expect_equal(
        repeated_sort(nullptr, 0, 3),
        0,
        "null empty input"
    ) && passed;

    const int placeholder = 17;
    passed = expect_equal(
        repeated_sort(&placeholder, 0, 3),
        0,
        "empty input"
    ) && passed;
    passed = expect_equal(
        repeated_sort(&placeholder, 1, 0),
        0,
        "zero rounds"
    ) && passed;
    passed = expect_equal(
        repeated_sort(&placeholder, 1, -5),
        0,
        "negative rounds"
    ) && passed;

    return passed;
}

bool test_fixed_cases(RepeatedSortFunction repeated_sort) {
    bool passed = true;

    const int single_positive[] = {9};
    passed = expect_case(
        repeated_sort,
        single_positive,
        1,
        4,
        "single positive value"
    ) && passed;

    const int single_negative[] = {-6};
    passed = expect_case(
        repeated_sort,
        single_negative,
        1,
        3,
        "single negative value"
    ) && passed;

    const int odd_unsorted[] = {5, -2, 9, 5, 0};
    passed = expect_case(
        repeated_sort,
        odd_unsorted,
        5,
        8,
        "odd unsorted values"
    ) && passed;

    const int even_unsorted[] = {10, -4, 11, -1};
    passed = expect_case(
        repeated_sort,
        even_unsorted,
        4,
        6,
        "even unsorted values"
    ) && passed;

    const int truncating_median[] = {-5, -2, 1, 8};
    passed = expect_case(
        repeated_sort,
        truncating_median,
        4,
        5,
        "even median truncates toward zero"
    ) && passed;

    const int duplicates[] = {3, 3, 3, -1, -1, 8, 8};
    passed = expect_case(
        repeated_sort,
        duplicates,
        7,
        16,
        "duplicates and round wraparound"
    ) && passed;

    const int extremes[] = {
        std::numeric_limits<int>::min(),
        -1,
        0,
        std::numeric_limits<int>::max()
    };
    passed = expect_case(
        repeated_sort,
        extremes,
        4,
        4,
        "integer extremes"
    ) && passed;

    return passed;
}

bool test_input_is_not_modified(RepeatedSortFunction repeated_sort) {
    std::array<int, 6> input = {4, -8, 15, 16, 23, 42};
    const std::array<int, 6> original = input;

    const bool result_matches = expect_case(
        repeated_sort,
        input.data(),
        input.size(),
        11,
        "input preservation result"
    );

    if (input == original) {
        return result_matches;
    }

    std::cerr << "repeated_sort input preservation failed: input was modified\n";
    return false;
}

bool test_generated_cases(RepeatedSortFunction repeated_sort) {
    bool passed = true;

    for (std::size_t length = 1; length <= 16; ++length) {
        std::vector<int> input(length);
        for (std::size_t i = 0; i < input.size(); ++i) {
            input[i] = static_cast<int>(((i * 37 + length * 11) % 29) - 14);
        }

        for (int rounds : {1, 2, 3, 7, 16, 31}) {
            passed = expect_case(
                repeated_sort,
                input.data(),
                input.size(),
                rounds,
                "generated oracle comparison"
            ) && passed;
        }
    }

    return passed;
}

} // namespace

bool run_repeated_sort_tests(RepeatedSortFunction repeated_sort) {
    if (repeated_sort == nullptr) {
        std::cerr << "repeated_sort function pointer is null\n";
        return false;
    }

    bool passed = true;
    passed = test_edge_cases(repeated_sort) && passed;
    passed = test_fixed_cases(repeated_sort) && passed;
    passed = test_input_is_not_modified(repeated_sort) && passed;
    passed = test_generated_cases(repeated_sort) && passed;

    return passed;
}
