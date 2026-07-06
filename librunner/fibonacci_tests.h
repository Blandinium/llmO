#ifndef LIBRUNNER_FIBONACCI_TESTS_H
#define LIBRUNNER_FIBONACCI_TESTS_H

#include <cstdint>

using FibonacciFunction = std::uint64_t (*)(std::uint64_t);

bool run_fibonacci_tests(FibonacciFunction fibonacci);

#endif // LIBRUNNER_FIBONACCI_TESTS_H
