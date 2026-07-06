#ifndef LLMO_SUT_API_H
#define LLMO_SUT_API_H

#include "library.h"

using Fibonacci = uint64_t (*)(uint64_t);
using FormatList = char* (*)(const int*, size_t);
using RepeatedSort = int64_t (*)(const int*, size_t, int);
using CountMatches = size_t (*)(const int*, size_t, const int*, size_t);
using TopWordsFromFile = WordCount* (*)(
    const char*,
    const char* const*,
    size_t,
    size_t,
    size_t*
);
using FreeString = void (*)(char*);
using FreeWordCounts = void (*)(WordCount*, size_t);

struct SutApi {
    Fibonacci fibonacci = nullptr;
    FormatList format_list = nullptr;
    RepeatedSort repeated_sort = nullptr;
    CountMatches count_matches = nullptr;
    TopWordsFromFile top_words_from_file = nullptr;
    FreeString free_string = nullptr;
    FreeWordCounts free_word_counts = nullptr;
};

#endif //LLMO_SUT_API_H
