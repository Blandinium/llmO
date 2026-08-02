#include "library.h"
#include "sut_common.h"

#include <algorithm>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

static bool should_ignore(
    const std::unordered_set<std::string>& ignore,
    const std::string& word
) {
    return ignore.find(word) != ignore.end();
}

static void scan_text(
    const std::string& text,
    std::unordered_map<std::string, std::uint64_t>& frequencies,
    const std::unordered_set<std::string>& ignore
) {
    std::string current_word;
    for (size_t i = 0; i < text.size(); ++i) {
        char c = text[i];
        if (is_word_char(c)) {
            current_word.push_back(normalize_char(c));
        } else {
            if (!current_word.empty() && !should_ignore(ignore, current_word)) {
                frequencies[current_word]++;
            }
            current_word.clear();
        }
    }
    if (!current_word.empty() && !should_ignore(ignore, current_word)) {
        frequencies[current_word]++;
    }
}

static bool is_better_candidate(const WordCount& a, const WordCount& b) {
    if (a.count != b.count) {
        return a.count > b.count;
    }
    return std::strcmp(a.word, b.word) < 0;
}

static void consider_candidate(
    WordCount* top,
    size_t top_length,
    const std::string& word,
    std::uint64_t count
) {
    char* candidate_word = copy_to_c_string(word);
    if (candidate_word == nullptr) {
        throw std::bad_alloc();
    }

    WordCount candidate{candidate_word, count};

    const auto insert_pos = std::lower_bound(
        top,
        top + top_length,
        candidate,
        [](const WordCount& existing, const WordCount& value) {
            return is_better_candidate(existing, value);
        }
    );

    if (insert_pos == top + top_length) {
        std::free(candidate.word);
        return;
    }

    std::free((top + top_length - 1)->word);
    std::move_backward(insert_pos, top + top_length - 1, top + top_length);
    *insert_pos = candidate;
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
        std::unordered_set<std::string> ignore;
        for (size_t i = 0; i < ignore_words_length; ++i) {
            if (ignore_words[i] != nullptr) {
                ignore.emplace(ignore_words[i]);
            }
        }

        std::ifstream file(path, std::ios::in | std::ios::binary | std::ios::ate);
        if (!file) {
            return nullptr;
        }

        const std::streamsize size = file.tellg();
        file.seekg(0, std::ios::beg);

        std::string text(size, '\0');
        file.read(&text[0], size);
        file.close();

        std::unordered_map<std::string, std::uint64_t> frequencies;

        scan_text(text, frequencies, ignore);

        std::vector<std::pair<std::string, std::uint64_t>> frequency_items;
        frequency_items.reserve(frequencies.size());

        for (const auto& [word, count] : frequencies) {
            frequency_items.emplace_back(word, count);
        }

        std::sort(frequency_items.begin(), frequency_items.end(), 
            [](const auto& a, const auto& b) {
                if (a.second != b.second) {
                    return a.second > b.second;
                }
                return a.first < b.first;
            });

        const size_t result_size = std::min(frequency_items.size(), max_results);
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

        for (size_t i = 0; i < result_size; ++i) {
            consider_candidate(result, result_size, frequency_items[i].first, frequency_items[i].second);
        }

        if (result_length != nullptr) {
            *result_length = result_size;
        }

        return result_guard.release();
    } catch (...) {
        return nullptr;
    }
}

}
