#include "top_words_from_file_tests.h"

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <string_view>
#include <unistd.h>
#include <vector>

namespace {

struct ExpectedWordCount {
    std::string_view word;
    std::uint64_t count;
};

class TemporaryTextFile {
public:
    explicit TemporaryTextFile(std::string_view contents)
        : path_(std::filesystem::temp_directory_path() /
            ("llmo_top_words_test_" + std::to_string(getpid()) + "_" +
             std::to_string(next_id_) + ".txt")) {
        ++next_id_;

        std::ofstream file(path_, std::ios::binary);
        file << contents;
    }

    ~TemporaryTextFile() {
        std::error_code ignored;
        std::filesystem::remove(path_, ignored);
    }

    const char* c_str() const {
        path_string_ = path_.string();
        return path_string_.c_str();
    }

    TemporaryTextFile(const TemporaryTextFile&) = delete;
    TemporaryTextFile& operator=(const TemporaryTextFile&) = delete;

private:
    static inline int next_id_ = 0;

    std::filesystem::path path_;
    mutable std::string path_string_;
};

bool expect_top_words(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts,
    const char* path,
    const char* const* ignore_words,
    std::size_t ignore_words_length,
    std::size_t max_results,
    std::initializer_list<ExpectedWordCount> expected,
    const char* case_name
) {
    std::size_t actual_length = 12345;
    WordCount* actual = top_words_from_file(
        path,
        ignore_words,
        ignore_words_length,
        max_results,
        &actual_length
    );

    if (expected.size() == 0) {
        if (actual == nullptr && actual_length == 0) {
            return true;
        }

        std::cerr << "top_words_from_file " << case_name
                  << " failed: expected empty result, got length "
                  << actual_length << '\n';
        free_word_counts(actual, actual_length);
        return false;
    }

    if (actual == nullptr) {
        std::cerr << "top_words_from_file " << case_name
                  << " failed: returned nullptr\n";
        return false;
    }

    bool passed = true;
    if (actual_length != expected.size()) {
        std::cerr << "top_words_from_file " << case_name
                  << " failed: expected length " << expected.size()
                  << ", got " << actual_length << '\n';
        passed = false;
    }

    std::size_t index = 0;
    for (const ExpectedWordCount expected_entry : expected) {
        if (index >= actual_length) {
            passed = false;
            break;
        }

        const char* actual_word = actual[index].word != nullptr
            ? actual[index].word
            : "<null>";
        if (actual[index].word == nullptr ||
            expected_entry.word != actual_word ||
            expected_entry.count != actual[index].count) {
            std::cerr << "top_words_from_file " << case_name
                      << " failed at index " << index << ": expected "
                      << expected_entry.word << '=' << expected_entry.count
                      << ", got " << actual_word << '='
                      << actual[index].count << '\n';
            passed = false;
        }

        ++index;
    }

    free_word_counts(actual, actual_length);
    return passed;
}

bool expect_null_result(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts,
    const char* path,
    const char* const* ignore_words,
    std::size_t ignore_words_length,
    std::size_t max_results,
    const char* case_name
) {
    std::size_t actual_length = 12345;
    WordCount* actual = top_words_from_file(
        path,
        ignore_words,
        ignore_words_length,
        max_results,
        &actual_length
    );

    if (actual == nullptr && actual_length == 0) {
        return true;
    }

    std::cerr << "top_words_from_file " << case_name
              << " failed: expected nullptr and length 0, got length "
              << actual_length << '\n';
    free_word_counts(actual, actual_length);
    return false;
}

bool test_invalid_inputs(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    bool passed = true;

    const char* ignore[] = {"the"};
    passed = expect_null_result(
        top_words_from_file,
        free_word_counts,
        nullptr,
        ignore,
        1,
        3,
        "null path"
    ) && passed;

    TemporaryTextFile file("alpha beta");
    passed = expect_null_result(
        top_words_from_file,
        free_word_counts,
        file.c_str(),
        nullptr,
        1,
        3,
        "null ignore list with non-zero length"
    ) && passed;

    const std::filesystem::path missing_path =
        std::filesystem::temp_directory_path() /
        ("llmo_top_words_missing_" + std::to_string(getpid()) + ".txt");
    passed = expect_null_result(
        top_words_from_file,
        free_word_counts,
        missing_path.string().c_str(),
        nullptr,
        0,
        3,
        "missing file"
    ) && passed;

    return passed;
}

bool test_empty_results(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    bool passed = true;

    TemporaryTextFile empty_file("");
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        empty_file.c_str(),
        nullptr,
        0,
        5,
        {},
        "empty file"
    ) && passed;

    TemporaryTextFile punctuation_file("1234 --- !!! ...");
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        punctuation_file.c_str(),
        nullptr,
        0,
        5,
        {},
        "no alphabetic words"
    ) && passed;

    TemporaryTextFile zero_limit_file("alpha beta alpha");
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        zero_limit_file.c_str(),
        nullptr,
        0,
        0,
        {},
        "zero max results"
    ) && passed;

    const char* ignore[] = {"alpha", "beta"};
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        zero_limit_file.c_str(),
        ignore,
        2,
        5,
        {},
        "all words ignored"
    ) && passed;

    return passed;
}

bool test_counting_and_ordering(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    bool passed = true;

    TemporaryTextFile file(
        "Banana apple banana. Cherry apple banana! "
        "date cherry apple elderberry fig fig."
    );
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        file.c_str(),
        nullptr,
        0,
        5,
        {
            {"apple", 3},
            {"banana", 3},
            {"cherry", 2},
            {"fig", 2},
            {"date", 1},
        },
        "counting and tie ordering"
    ) && passed;

    TemporaryTextFile limit_file("delta gamma beta alpha delta gamma beta delta");
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        limit_file.c_str(),
        nullptr,
        0,
        2,
        {
            {"delta", 3},
            {"beta", 2},
        },
        "max result limit"
    ) && passed;

    return passed;
}

bool test_normalization_and_ignores(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    bool passed = true;

    TemporaryTextFile file(
        "The quick, QUICK; brown-fox cant stop the_the fox. "
        "CANT brown quick 42fox"
    );
    const char* ignore[] = {"THE", "can't", nullptr, "___"};
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        file.c_str(),
        ignore,
        4,
        6,
        {
            {"fox", 3},
            {"quick", 3},
            {"brown", 2},
            {"stop", 1},
        },
        "normalization and ignored words"
    ) && passed;

    TemporaryTextFile separator_file("co-op CO_op re-enter re2enter X.Y.z");
    passed = expect_top_words(
        top_words_from_file,
        free_word_counts,
        separator_file.c_str(),
        nullptr,
        0,
        10,
        {
            {"co", 2},
            {"enter", 2},
            {"op", 2},
            {"re", 2},
            {"x", 1},
            {"y", 1},
            {"z", 1},
        },
        "non-letter separators"
    ) && passed;

    return passed;
}

bool test_null_result_length(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    TemporaryTextFile file("alpha beta alpha");
    WordCount* result = top_words_from_file(
        file.c_str(),
        nullptr,
        0,
        2,
        nullptr
    );

    if (result == nullptr) {
        std::cerr << "top_words_from_file null result_length failed: returned nullptr\n";
        return false;
    }

    const bool passed = result[0].word != nullptr &&
        std::string_view(result[0].word) == "alpha" &&
        result[0].count == 2 &&
        result[1].word != nullptr &&
        std::string_view(result[1].word) == "beta" &&
        result[1].count == 1;

    if (!passed) {
        std::cerr << "top_words_from_file null result_length failed: unexpected result\n";
    }

    free_word_counts(result, 2);
    return passed;
}

} // namespace

bool run_top_words_from_file_tests(
    TopWordsFromFileFunction top_words_from_file,
    FreeWordCountsFunction free_word_counts
) {
    if (top_words_from_file == nullptr) {
        std::cerr << "top_words_from_file function pointer is null\n";
        return false;
    }
    if (free_word_counts == nullptr) {
        std::cerr << "free_word_counts function pointer is null\n";
        return false;
    }

    bool passed = true;
    passed = test_invalid_inputs(top_words_from_file, free_word_counts) && passed;
    passed = test_empty_results(top_words_from_file, free_word_counts) && passed;
    passed = test_counting_and_ordering(top_words_from_file, free_word_counts) &&
        passed;
    passed = test_normalization_and_ignores(top_words_from_file, free_word_counts) &&
        passed;
    passed = test_null_result_length(top_words_from_file, free_word_counts) && passed;

    return passed;
}
