#include "library.h"
#include "sut_common.h"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <unordered_map>
#include <vector>

namespace {
    struct WordCountPair {
        std::string word;
        uint64_t count;
    };

    bool should_ignore(
        const std::vector<std::string_view>& ignore,
        std::string_view word
    ) {
        return std::ranges::any_of(ignore, [&word](const std::string_view& ignored_word) {
            return ignored_word == word;
        });
    }

    void add_word(
        std::unordered_map<std::string, uint64_t>& frequencies,
        const std::vector<std::string_view>& ignore,
        std::string_view word
    ) {
        if (!word.empty() && !should_ignore(ignore, word)) {
            frequencies[std::string(word)]++;
        }
    }

    void scan_text(
        std::string_view text,
        std::unordered_map<std::string, uint64_t>& frequencies,
        const std::vector<std::string_view>& ignore
    ) {
        std::string current_word;
        current_word.reserve(32); // Reserve space to reduce reallocations

        for (size_t i = 0; i < text.size(); ++i) {
            const char c = text[i];
            if (is_word_char(c)) {
                current_word.push_back(normalize_char(c));
            } else {
                add_word(frequencies, ignore, current_word);
                current_word.clear();
            }
        }
        add_word(frequencies, ignore, current_word);
    }

    bool is_better_candidate(const WordCount& a, const WordCount& b) {
        if (a.count != b.count) {
            return a.count > b.count;
        }
        return std::strcmp(a.word, b.word) < 0;
    }

    void consider_candidate(
        WordCount* top,
        size_t top_length,
        std::string&& word,
        uint64_t count
    ) {
        char* candidate_word = copy_to_c_string(std::move(word));
        if (candidate_word == nullptr) {
            throw std::bad_alloc();
        }

        WordCount candidate{candidate_word, count};
        auto insert_pos = std::ranges::lower_bound(
            top,
            top + top_length,
            candidate,
            [](const WordCount& existing, const WordCount& value) {
                return is_better_candidate(existing, value);
            }
        );

        if (insert_pos == top + top_length) {
            std::free(candidate_word);
            return;
        }

        std::free((top + top_length - 1)->word);
        std::move_backward(insert_pos, top + top_length - 1, top + top_length);
        *insert_pos = candidate;
    }

    void find_top(
        std::unordered_map<std::string, uint64_t>& frequencies,
        WordCount* top,
        size_t top_length
    ) {
        std::vector<std::pair<std::string, uint64_t>> frequency_items;
        frequency_items.reserve(frequencies.size());
        for (auto&& [word, count] : frequencies) {
            frequency_items.emplace_back(std::move(word), count);
        }

        std::sort(frequency_items.begin(), frequency_items.end(),
            [](const auto& a, const auto& b) {
                if (a.second != b.second) {
                    return a.second > b.second;
                }
                return a.first < b.first;
            });

        for (size_t i = 0; i < frequency_items.size() && i < top_length; ++i) {
            consider_candidate(top, top_length, std::move(frequency_items[i].first), frequency_items[i].second);
        }
    }

    std::string read_whole_file(const std::string& path) {
        std::ifstream file(path, std::ios::binary);
        if (!file) {
            throw std::runtime_error("Could not open input file: " + path);
        }

        file.seekg(0, std::ios::end);
        const std::streamsize size = file.tellg();
        if (size < 0) {
            throw std::runtime_error("Could not determine input file size: " + path);
        }
        file.seekg(0, std::ios::beg);

        std::string contents;
        contents.resize(static_cast<std::size_t>(size));
        if (size > 0) {
            file.read(contents.data(), size);
            if (!file) {
                throw std::runtime_error("Could not read input file: " + path);
            }
        }
        return contents;
    }
}

extern "C" {

WordCount* top_words_from_file(
    const char* path,
    const char* const* ignore_words,
    size_t ignore_words_length,
    size_t max_results,
    size_t* result_length
) {
    if (result_length != nullptr) {
        *result_length = 0;
    }

    if (path == nullptr || (ignore_words == nullptr && ignore_words_length != 0)) {
        return nullptr;
    }

    try {
        std::vector<std::string_view> ignore;
        ignore.reserve(ignore_words_length);

        for (size_t i = 0; i < ignore_words_length; ++i) {
            if (ignore_words[i] != nullptr) {
                ignore.emplace_back(ignore_words[i]);
            }
        }

        const std::string text = read_whole_file(path);

        std::unordered_map<std::string, uint64_t> frequencies;
        scan_text(text, frequencies, ignore);

        const size_t result_size = std::min(frequencies.size(), max_results);
        if (result_size == 0) {
            return nullptr;
        }

        WordCount* result = static_cast<WordCount*>(
            std::calloc(result_size, sizeof(WordCount))
        );
        if (result == nullptr) {
            return nullptr;
        }

        const auto cleanup = [result_size](WordCount* values) {
            free_word_counts(values, result_size);
        };
        std::unique_ptr<WordCount, decltype(cleanup)> result_guard(result, cleanup);

        find_top(frequencies, result, result_size);

        if (result_length != nullptr) {
            *result_length = result_size;
        }

        return result_guard.release();
    } catch (...) {
        return nullptr;
    }
}
}
