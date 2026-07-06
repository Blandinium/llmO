#include "fibonacci_tests.h"

#include <array>
#include <cstdint>
#include <iostream>

namespace {

bool expect_equal(
    std::uint64_t actual,
    std::uint64_t expected,
    const char* check_name,
    std::uint64_t n
) {
    if (actual == expected) {
        return true;
    }

    std::cerr << "fibonacci " << check_name << " failed for n=" << n
              << ": expected " << expected << ", got " << actual << '\n';
    return false;
}

std::uint64_t iterative_fibonacci(std::uint64_t n) {
    std::uint64_t previous = 0;
    std::uint64_t current = 1;

    for (std::uint64_t i = 0; i < n; ++i) {
        const std::uint64_t next = previous + current;
        previous = current;
        current = next;
    }

    return previous;
}

bool test_known_values(FibonacciFunction fibonacci) {
    constexpr std::array<std::uint64_t, 31> expected_values = {
        0,
        1,
        1,
        2,
        3,
        5,
        8,
        13,
        21,
        34,
        55,
        89,
        144,
        233,
        377,
        610,
        987,
        1597,
        2584,
        4181,
        6765,
        10946,
        17711,
        28657,
        46368,
        75025,
        121393,
        196418,
        317811,
        514229,
        832040,
    };

    bool passed = true;
    for (std::uint64_t n = 0; n < expected_values.size(); ++n) {
        passed = expect_equal(fibonacci(n), expected_values[n], "known value", n) &&
            passed;
    }

    return passed;
}

bool test_against_independent_oracle(FibonacciFunction fibonacci) {
    bool passed = true;

    for (std::uint64_t n = 0; n <= 35; ++n) {
        passed = expect_equal(fibonacci(n), iterative_fibonacci(n), "oracle", n) &&
            passed;
    }

    return passed;
}

bool test_recurrence(FibonacciFunction fibonacci) {
    bool passed = true;

    for (std::uint64_t n = 2; n <= 30; ++n) {
        const std::uint64_t expected = fibonacci(n - 1) + fibonacci(n - 2);
        passed = expect_equal(fibonacci(n), expected, "recurrence", n) && passed;
    }

    return passed;
}

bool test_monotonic_growth(FibonacciFunction fibonacci) {
    for (std::uint64_t n = 2; n <= 30; ++n) {
        const std::uint64_t previous = fibonacci(n - 1);
        const std::uint64_t current = fibonacci(n);
        if (current < previous) {
            std::cerr << "fibonacci monotonic growth failed for n=" << n
                      << ": fibonacci(n - 1)=" << previous
                      << ", fibonacci(n)=" << current << '\n';
            return false;
        }
    }

    return true;
}

bool test_addition_identity(FibonacciFunction fibonacci) {
    bool passed = true;

    for (std::uint64_t n = 2; n <= 12; ++n) {
        for (std::uint64_t k = 1; k <= 8; ++k) {
            const std::uint64_t expected =
                fibonacci(k) * fibonacci(n + 1) +
                fibonacci(k - 1) * fibonacci(n);
            const std::uint64_t index = n + k;

            passed = expect_equal(fibonacci(index), expected, "addition identity", index) &&
                passed;
        }
    }

    return passed;
}

bool test_parity_pattern(FibonacciFunction fibonacci) {
    for (std::uint64_t n = 0; n <= 30; ++n) {
        const bool expected_even = n % 3 == 0;
        const bool actual_even = fibonacci(n) % 2 == 0;
        if (actual_even != expected_even) {
            std::cerr << "fibonacci parity pattern failed for n=" << n
                      << ": expected " << (expected_even ? "even" : "odd")
                      << ", got " << (actual_even ? "even" : "odd") << '\n';
            return false;
        }
    }

    return true;
}

} // namespace

bool run_fibonacci_tests(FibonacciFunction fibonacci) {
    if (fibonacci == nullptr) {
        std::cerr << "fibonacci function pointer is null\n";
        return false;
    }

    bool passed = true;
    passed = test_known_values(fibonacci) && passed;
    passed = test_against_independent_oracle(fibonacci) && passed;
    passed = test_recurrence(fibonacci) && passed;
    passed = test_monotonic_growth(fibonacci) && passed;
    passed = test_addition_identity(fibonacci) && passed;
    passed = test_parity_pattern(fibonacci) && passed;

    return passed;
}
