#include "count_matches_tests.h"

#include <array>
#include <iostream>
#include <limits>
#include <vector>

namespace {

bool contains(const int* values, std::size_t length, int needle) {
    for (std::size_t i = 0; i < length; ++i) {
        if (values[i] == needle) {
            return true;
        }
    }

    return false;
}

std::size_t oracle_count_matches(
    const int* allowed,
    std::size_t allowed_length,
    const int* queries,
    std::size_t queries_length
) {
    if ((allowed == nullptr && allowed_length != 0) ||
        (queries == nullptr && queries_length != 0)) {
        return 0;
    }

    std::size_t matches = 0;
    for (std::size_t i = 0; i < queries_length; ++i) {
        if (contains(allowed, allowed_length, queries[i])) {
            ++matches;
        }
    }

    return matches;
}

bool expect_equal(
    std::size_t actual,
    std::size_t expected,
    const char* case_name
) {
    if (actual == expected) {
        return true;
    }

    std::cerr << "count_matches " << case_name << " failed: expected "
              << expected << ", got " << actual << '\n';
    return false;
}

bool expect_case(
    CountMatchesFunction count_matches,
    const int* allowed,
    std::size_t allowed_length,
    const int* queries,
    std::size_t queries_length,
    const char* case_name
) {
    return expect_equal(
        count_matches(allowed, allowed_length, queries, queries_length),
        oracle_count_matches(allowed, allowed_length, queries, queries_length),
        case_name
    );
}

bool test_edge_cases(CountMatchesFunction count_matches) {
    bool passed = true;

    const int placeholder = 1;
    passed = expect_equal(
        count_matches(nullptr, 3, &placeholder, 1),
        0,
        "null allowed with non-zero length"
    ) && passed;
    passed = expect_equal(
        count_matches(&placeholder, 1, nullptr, 3),
        0,
        "null queries with non-zero length"
    ) && passed;
    passed = expect_equal(
        count_matches(nullptr, 3, nullptr, 3),
        0,
        "both null with non-zero lengths"
    ) && passed;
    passed = expect_case(
        count_matches,
        nullptr,
        0,
        nullptr,
        0,
        "both empty null inputs"
    ) && passed;
    passed = expect_case(
        count_matches,
        &placeholder,
        0,
        &placeholder,
        0,
        "both empty non-null inputs"
    ) && passed;

    const int queries[] = {1, 2, 3};
    passed = expect_case(
        count_matches,
        nullptr,
        0,
        queries,
        3,
        "empty allowed"
    ) && passed;
    passed = expect_case(
        count_matches,
        &placeholder,
        1,
        nullptr,
        0,
        "empty queries"
    ) && passed;

    return passed;
}

bool test_fixed_cases(CountMatchesFunction count_matches) {
    bool passed = true;

    const int allowed[] = {1, 3, 5, 7};
    const int queries[] = {0, 1, 2, 3, 7, 9};
    passed = expect_case(
        count_matches,
        allowed,
        4,
        queries,
        6,
        "mixed hits and misses"
    ) && passed;

    const int duplicate_allowed[] = {4, 4, 4, -2, -2, 10};
    const int duplicate_queries[] = {4, 4, -2, -2, -2, 10, 11};
    passed = expect_case(
        count_matches,
        duplicate_allowed,
        6,
        duplicate_queries,
        7,
        "duplicates count per query"
    ) && passed;

    const int negative_allowed[] = {-10, -5, 0, 5};
    const int negative_queries[] = {-10, -9, -5, 0, 5, 6};
    passed = expect_case(
        count_matches,
        negative_allowed,
        4,
        negative_queries,
        6,
        "negative and zero values"
    ) && passed;

    const int extremes_allowed[] = {
        std::numeric_limits<int>::min(),
        -1,
        std::numeric_limits<int>::max()
    };
    const int extremes_queries[] = {
        std::numeric_limits<int>::max(),
        0,
        std::numeric_limits<int>::min(),
        std::numeric_limits<int>::min()
    };
    passed = expect_case(
        count_matches,
        extremes_allowed,
        3,
        extremes_queries,
        4,
        "integer extremes"
    ) && passed;

    return passed;
}

bool test_input_is_not_modified(CountMatchesFunction count_matches) {
    std::array<int, 5> allowed = {8, 6, 7, 5, 3};
    std::array<int, 6> queries = {3, 0, 9, 8, 6, 1};
    const std::array<int, 5> original_allowed = allowed;
    const std::array<int, 6> original_queries = queries;

    const bool result_matches = expect_case(
        count_matches,
        allowed.data(),
        allowed.size(),
        queries.data(),
        queries.size(),
        "input preservation result"
    );

    if (allowed == original_allowed && queries == original_queries) {
        return result_matches;
    }

    std::cerr << "count_matches input preservation failed: input was modified\n";
    return false;
}

bool test_generated_cases(CountMatchesFunction count_matches) {
    bool passed = true;

    for (std::size_t allowed_length = 1; allowed_length <= 12; ++allowed_length) {
        std::vector<int> allowed(allowed_length);
        for (std::size_t i = 0; i < allowed.size(); ++i) {
            allowed[i] = static_cast<int>(((i * 17 + allowed_length * 5) % 23) - 11);
        }

        for (std::size_t queries_length = 1; queries_length <= 15; ++queries_length) {
            std::vector<int> queries(queries_length);
            for (std::size_t i = 0; i < queries.size(); ++i) {
                queries[i] = static_cast<int>(
                    ((i * 31 + queries_length * 7 + allowed_length) % 29) - 14
                );
            }

            passed = expect_case(
                count_matches,
                allowed.data(),
                allowed.size(),
                queries.data(),
                queries.size(),
                "generated oracle comparison"
            ) && passed;
        }
    }

    return passed;
}

} // namespace

bool run_count_matches_tests(CountMatchesFunction count_matches) {
    if (count_matches == nullptr) {
        std::cerr << "count_matches function pointer is null\n";
        return false;
    }

    bool passed = true;
    passed = test_edge_cases(count_matches) && passed;
    passed = test_fixed_cases(count_matches) && passed;
    passed = test_input_is_not_modified(count_matches) && passed;
    passed = test_generated_cases(count_matches) && passed;

    return passed;
}
