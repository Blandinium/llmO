#ifndef SUT_LIBRARY_H
#define SUT_LIBRARY_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct WordCount {
    char* word;
    uint64_t count;
} WordCount;

uint64_t fibonacci(uint64_t n);
char* format_list(const int* input, size_t input_length);
int64_t repeated_sort(const int* input, size_t input_length, int rounds);
size_t count_matches(
    const int* allowed,
    size_t allowed_length,
    const int* queries,
    size_t queries_length
);
WordCount* top_words_from_file(
    const char* path,
    const char* const* ignore_words,
    size_t ignore_words_length,
    size_t max_results,
    size_t* result_length
);
void free_string(char* value);
void free_word_counts(WordCount* values, size_t length);

#ifdef __cplusplus
}
#endif

#endif // SUT_LIBRARY_H
