#ifndef LLMO_BENCHMARKS_H
#define LLMO_BENCHMARKS_H

#include "sut_api.h"

void benchmark_fibonacci(const SutApi& api);
void benchmark_format_list(const SutApi& api);
void benchmark_repeated_sort(const SutApi& api);
void benchmark_count_matches(const SutApi& api);
void benchmark_top_words_from_file(const SutApi& api);

#endif //LLMO_BENCHMARKS_H
