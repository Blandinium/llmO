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

namespace {

struct WordCountPair {
    std::string word;
    uint64_t count;
};

struct IgnoreWordHash {
    size_t operator()(const std::string& word) const {
        return std::hash<std::string>{}(word);
    }
};

struct IgnoreWordEqual {
    bool operator()(const std::string& lhs, const std::string& rhs) const {
        return lhs == rhs;
    }
};

static bool should_ignore(
    const std::unordered_map<std::string, bool, IgnoreWordHash, IgnoreWordEqual>& ignore,
    const std::string& word
) {
    return ignore.find(word) != ignore.end();
}

static void add_word(
    std::unordered_map<std::string, uint64_t>& frequencies,
    const std::unordered_map<std::string, bool, IgnoreWordHash, IgnoreWordEqual>& ignore,
    const std::string& word
) {
    if (!word.empty() && !should_ignore(ignore, word)) {
        frequencies[word] += 1;
    }
}

static void scan_text(
    const std::string& text,
    std::unordered_map<std::string, uint64_t>& frequencies,
    const std::unordered_map<std::string, bool, IgnoreWordHash, IgnoreWordEqual>& ignore
) {
    std::string current_word;
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
    uint64_t count
) {
    char* candidate_word = copy_to_c_string(word);
    if (candidate_word == nullptr) {
        throw std::bad_alloc();
    }

    WordCount candidate{candidate_word, count};

    auto insert_pos = std::lower_bound(
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

static void find_top(
    const std::vector<WordCountPair>& frequency_items,
    WordCount* top,
    size_t top_length
) {
    for (const auto& item : frequency_items) {
        consider_candidate(top, top_length, item.word, item.count);
    }
}

static std::string read_whole_file(const std::string& path) {
    std::ifstream file(path, std::ios::binary | std::ios::ate);
    if (!file) {
        throw std::runtime_error("Could not open input file: " + path);
    }

    const std::streamsize size = file.tellg();
    if (size < 0) {
        throw std::runtime_error("Could not determine input file size: " + path);
    }
    file.seekg(0, std::ios::beg);

    std::string contents;
    contents.resize(static_cast<std::size_t>(size));
    file.read(contents.data(), size);
    if (!file) {
        throw std::runtime_error("Could not read input file: " + path);
    }

    return contents;
}

} // namespace

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
        std::unordered_map<std::string, bool, IgnoreWordHash, IgnoreWordEqual> ignore;
        ignore.reserve(ignore_words_length);

        for (size_t i = 0; i < ignore_words_length; ++i) {
            if (ignore_words[i] != nullptr) {
                std::string normalized;
                normalized.reserve(32); // typical word length
                for (char c = *ignore_words[i]; c != '\0'; ++c) {
                    if (is_word_char(c)) {
                        normalized.push_back(normalize_char(c));
                    }
                }
                if (!normalized.empty()) {
                    ignore.emplace(std::move(normalized), true);
                }
            }
        }

        const std::string text = read_whole_file(path);
        std::unordered_map<std::string, uint64_t> frequencies;
        scan_text(text, frequencies, ignore);

        std::vector<WordCountPair> frequency_items;
        frequency_items.reserve(frequencies.size());
        for (auto&& [word, count] : frequencies) {
            frequency_items.emplace_back(std::move(word), count);
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
        const auto cleanup = [result_size](WordCount* values) {
            free_word_counts(values, result_size);
        };
        std::unique_ptr<WordCount, decltype(cleanup)> result_guard(result, cleanup);

        find_top(frequency_items, result, result_size);

        if (result_length != nullptr) {
            *result_length = result_size;
        }

        return result_guard.release();
    } catch (...) {
        return nullptr;
    }
}

} // extern "C"
