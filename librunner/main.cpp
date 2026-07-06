#include "library.h"
#include "fibonacci_tests.h"
#include "format_list_tests.h"
#include "repeated_sort_tests.h"
#include "count_matches_tests.h"
#include "top_words_from_file_tests.h"
#include "benchmarks.h"
#include "sut_api.h"

#include <dlfcn.h>
#include <charconv>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <string_view>

namespace {


void print_usage(const char* executable) {
    std::cerr << "Usage: " << executable << " <path-to-libSUT.so> <function-id>\n"
              << "function-id: 0=fibonacci, 1=format_list, 2=repeated_sort, "
              << "3=count_matches, 4=top_words_from_file\n";
}

struct LibraryHandle {
    void* handle = nullptr;

    explicit LibraryHandle(const char* path)
        : handle(dlopen(path, RTLD_NOW)) {}

    ~LibraryHandle() {
        if (handle != nullptr) {
            dlclose(handle);
        }
    }

    LibraryHandle(const LibraryHandle&) = delete;
    LibraryHandle& operator=(const LibraryHandle&) = delete;
};

template <typename Function>
Function load_symbol(void* library, const char* name) {
    dlerror();
    void* symbol = dlsym(library, name);
    const char* error = dlerror();
    if (error != nullptr) {
        std::cerr << "Could not load symbol " << name << ": " << error << '\n';
        return nullptr;
    }

    return reinterpret_cast<Function>(symbol);
}

bool load_api(void* library, SutApi& api) {
    api.fibonacci = load_symbol<Fibonacci>(library, "fibonacci");
    api.format_list = load_symbol<FormatList>(library, "format_list");
    api.repeated_sort = load_symbol<RepeatedSort>(library, "repeated_sort");
    api.count_matches = load_symbol<CountMatches>(library, "count_matches");
    api.top_words_from_file = load_symbol<TopWordsFromFile>(library, "top_words_from_file");
    api.free_string = load_symbol<FreeString>(library, "free_string");
    api.free_word_counts = load_symbol<FreeWordCounts>(library, "free_word_counts");

    return api.fibonacci != nullptr &&
        api.format_list != nullptr &&
        api.repeated_sort != nullptr &&
        api.count_matches != nullptr &&
        api.top_words_from_file != nullptr &&
        api.free_string != nullptr &&
        api.free_word_counts != nullptr;
}

bool parse_function_id(std::string_view value, int& function_id) {
    const char* begin = value.data();
    const char* end = value.data() + value.size();
    const auto [ptr, error] = std::from_chars(begin, end, function_id);
    return error == std::errc{} && ptr == end && function_id >= 0 && function_id <= 4;
}

bool run_tests(int function_id, const SutApi& api) {
    switch (function_id) {
        case 0:
            return run_fibonacci_tests(api.fibonacci);
        case 1:
            return run_format_list_tests(api.format_list, api.free_string);
        case 2:
            return run_repeated_sort_tests(api.repeated_sort);
        case 3:
            return run_count_matches_tests(api.count_matches);
        case 4:
            return run_top_words_from_file_tests(
                        api.top_words_from_file,
                        api.free_word_counts
                    );
        default:
            return false;
    }
}

void run_benchmark(int function_id, const SutApi& api) {
    switch (function_id) {
        case 0:
            benchmark_fibonacci(api);
            break;
        case 1:
            benchmark_format_list(api);
            break;
        case 2:
            benchmark_repeated_sort(api);
            break;
        case 3:
            benchmark_count_matches(api);
            break;
        case 4:
            benchmark_top_words_from_file(api);
            break;
        default:
            return;
    }
}

} // namespace

int main(int argc, char** argv) {
    if (argc != 3) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    int function_id = -1;
    if (!parse_function_id(argv[2], function_id)) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    LibraryHandle library(argv[1]);
    if (library.handle == nullptr) {
        std::cerr << "Could not open library: " << dlerror() << '\n';
        return EXIT_FAILURE;
    }

    SutApi api;
    if (!load_api(library.handle, api)) {
        return EXIT_FAILURE;
    }

    if (!run_tests(function_id, api)) {
        std::cerr << "Tests failed for function " << function_id << '\n';
        return EXIT_FAILURE;
    }

    run_benchmark(function_id, api);
    return EXIT_SUCCESS;
}
