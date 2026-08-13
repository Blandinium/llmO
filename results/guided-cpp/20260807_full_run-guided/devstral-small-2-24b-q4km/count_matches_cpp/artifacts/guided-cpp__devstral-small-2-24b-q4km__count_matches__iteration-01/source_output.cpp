#include "library.h"

#include <algorithm>
#include <bit>
#include <span>

static constexpr std::size_t BITS_PER_WORD = 64;
static constexpr std::size_t WORDS_PER_LONG = sizeof(unsigned long) * BITS_PER_WORD;

static bool contains(const std::span<const int> input, const int needle) {
    for (std::size_t i = 0; i < input.size(); ++i) {
        if (input[i] == needle) {
            return true;
        }
    }
    return false;
}

extern "C" {

size_t count_matches(
    const int* allowed,
    size_t allowed_length,
    const int* queries,
    size_t queries_length
) {
    if ((allowed == nullptr && allowed_length != 0) ||
        (queries == nullptr && queries_length != 0)) {
        return 0;
    }

    try {
        const std::span<const int> allowed_span{allowed, allowed_length};
        std::size_t matches = 0;

        for (std::size_t i = 0; i < queries_length; ++i) {
            if (contains(allowed_span, queries[i])) {
                ++matches;
            }
        }

        return matches;
    } catch (...) {
        return 0;
    }
}

}
