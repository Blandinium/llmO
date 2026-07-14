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
#include <vector>

static bool should_ignore(
    const std::vector<std::string>& ignore,
    const std::string& word
) {
    for (const std::string& ignored_word : ignore) {
        if (ignored_word == word) {
            return true;
        }
    }

    return false;
}

static void add_word(
    std::unordered_map<std::string, std::uint64_t>& frequencies,
    const std::vector<std::string>& ignore,
    const std::string& word
) {
    if (!word.empty() && !should_ignore(ignore, word)) {
        frequencies[word] += 1;
    }
}

static void scan_text_tail_recursive(
    const std::string& text,
    std::size_t index,
    std::string current_word,
    std::unordered_map<std::string, std::uint64_t>& frequencies,
    const std::vector<std::string>& ignore
) {
    if (index == text.size()) {
        add_word(frequencies, ignore, current_word);
        return;
    }

    const char c = text[index];

    if (is_word_char(c)) {
        current_word.push_back(normalize_char(c));

        scan_text_tail_recursive(
            text,
            index + 1,
            std::move(current_word),
            frequencies,
            ignore
        );

        return;
    }

    add_word(frequencies, ignore, current_word);

    scan_text_tail_recursive(
        text,
        index + 1,
        std::string{},
        frequencies,
        ignore
    );
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

    const auto insert_pos = std::ranges::lower_bound(
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

static void find_top_tail_recursive(
    std::vector<std::pair<std::string, std::uint64_t>>::const_iterator it,
    std::vector<std::pair<std::string, std::uint64_t>>::const_iterator end,
    WordCount* top,
    size_t top_length
) {
    if (it == end) {
        return;
    }

    consider_candidate(top, top_length, it->first, it->second);

    find_top_tail_recursive(it + 1, end, top, top_length);
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

        scan_text_tail_recursive(
            text,
            0,
            std::string{},
            frequencies,
            normalized_ignore
        );

        std::vector<std::pair<std::string, std::uint64_t>> frequency_items;
        frequency_items.reserve(frequencies.size());

        for (const auto& [word, count] : frequencies) {
            frequency_items.emplace_back(word, count);
        }

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

        for (size_t i = 0; i < result_size; ++i) {
            consider_candidate(result, result_size, frequency_items[i].first, frequency_items[i].second);
        }

        find_top_tail_recursive(
            frequency_items.begin() + result_size,
            frequency_items.end(),
            result,
            result_size
        );

        if (result_length != nullptr) {
            *result_length = result_size;
        }

        return result;
    } catch (...) {
        return nullptr;
    }
}

}
