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
#include <unordered_map>
#include <utility>
#include <vector>

static bool should_ignore(
    const std::vector<std::string>& ignore,
    const std::string& word,
    std::size_t index
) {
    for (; index < ignore.size(); ++index) {
        if (ignore[index] == word) {
            return true;
        }
    }
    return false;
}

static void add_word(
    std::unordered_map<std::string, std::uint64_t>& frequencies,
    const std::vector<std::string>& ignore,
    const std::string& word,
    std::size_t& ignore_index
) {
    if (!word.empty() && !should_ignore(ignore, word, ignore_index)) {
        frequencies[word] += 1;
    }
}

static void scan_text(
    const std::string& text,
    std::unordered_map<std::string, std::uint64_t>& frequencies,
    const std::vector<std::string>& ignore,
    std::size_t& ignore_index
) {
    std::string current_word;
    current_word.reserve(32); // Pre-allocate to reduce reallocations

    for (std::size_t i = 0; i < text.size(); ++i) {
        const char c = text[i];

        if (is_word_char(c)) {
            current_word.push_back(normalize_char(c));
        } else {
            add_word(frequencies, ignore, current_word, ignore_index);
            current_word.clear();
        }
    }
    add_word(frequencies, ignore, current_word, ignore_index);
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
    size_t insert_pos = top_length;

    for (size_t i = 0; i < top_length; ++i) {
        if (is_better_candidate(top[i], candidate)) {
            break;
        }
        insert_pos = i;
    }

    if (insert_pos < top_length) {
        std::free(top[top_length - 1].word);
        std::move_backward(top + insert_pos, top + top_length - 1, top + top_length);
        top[insert_pos] = candidate;
    } else {
        std::free(candidate_word);
    }
}

static void find_top(
    const std::vector<std::pair<std::string, std::uint64_t>>& frequency_items,
    WordCount* top,
    size_t top_length
) {
    for (size_t i = top_length; i < frequency_items.size(); ++i) {
        consider_candidate(top, top_length, frequency_items[i].first, frequency_items[i].second);
    }
}

static std::string read_whole_file(const std::string& path) {
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
        std::vector<std::string> ignore;
        ignore.reserve(ignore_words_length);

        for (size_t i = 0; i < ignore_words_length; ++i) {
            if (ignore_words[i] != nullptr) {
                ignore.emplace_back(ignore_words[i]);
            }
        }

        const std::string text = read_whole_file(path);

        std::vector<std::string> normalized_ignore;
        normalized_ignore.reserve(ignore.size());

        for (const std::string& word : ignore) {
            std::string normalized;
            normalized.reserve(word.size());

            for (char c : word) {
                if (is_word_char(c)) {
                    normalized.push_back(normalize_char(c));
                }
            }

            if (!normalized.empty()) {
                normalized_ignore.push_back(std::move(normalized));
            }
        }

        std::unordered_map<std::string, std::uint64_t> frequencies;
        std::size_t ignore_index = 0;

        scan_text(text, frequencies, normalized_ignore, ignore_index);

        std::vector<std::pair<std::string, std::uint64_t>> frequency_items;
        frequency_items.reserve(frequencies.size());
        frequency_items.insert(frequency_items.end(), frequencies.begin(), frequencies.end());

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

        find_top(frequency_items, result, result_size);

        if (result_length != nullptr) {
            *result_length = result_size;
        }

        return result_guard.release();
    } catch (...) {
        return nullptr;
    }
}

}
