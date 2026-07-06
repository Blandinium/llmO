#ifndef LIBRUNNER_COUNT_MATCHES_TESTS_H
#define LIBRUNNER_COUNT_MATCHES_TESTS_H

#include <cstddef>

using CountMatchesFunction = std::size_t (*)(
    const int*,
    std::size_t,
    const int*,
    std::size_t
);

bool run_count_matches_tests(CountMatchesFunction count_matches);

#endif // LIBRUNNER_COUNT_MATCHES_TESTS_H
