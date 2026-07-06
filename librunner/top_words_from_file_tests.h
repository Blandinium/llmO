#ifndef LIBRUNNER_TOP_WORDS_FROM_FILE_TESTS_H
#define LIBRUNNER_TOP_WORDS_FROM_FILE_TESTS_H

#include "library.h"

#include <cstddef>

using TopWordsFromFileFunction = WordCount* (*)(
    const char*,
    const char* const*,
    std::size_t,
    std::size_t,
    std::size_t*
);
using FreeWordCountsFunction = void (*)(WordCount*, std::size_t);

bool run_top_words_from_file_tests(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
);

#endif // LIBRUNNER_TOP_WORDS_FROM_FILE_TESTS_H
