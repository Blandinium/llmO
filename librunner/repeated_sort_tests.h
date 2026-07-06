#ifndef LIBRUNNER_REPEATED_SORT_TESTS_H
#define LIBRUNNER_REPEATED_SORT_TESTS_H

#include <cstddef>
#include <cstdint>

using RepeatedSortFunction = std::int64_t (*)(const int*, std::size_t, int);

bool run_repeated_sort_tests(RepeatedSortFunction repeated_sort);

#endif // LIBRUNNER_REPEATED_SORT_TESTS_H
