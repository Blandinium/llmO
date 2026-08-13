#include "library.h"
#include <algorithm>
#include <cstddef>
#include <cstring>
#include <array>
#include <vector>

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

    if (queries_length == 0 || allowed_length == 0) {
        return 0;
    }

    constexpr size_t small_threshold = 16;
    std::array<int, small_threshold> small_allowed;
    bool use_small_array = (allowed_length <= small_threshold);

    if (use_small_array) {
        std::memcpy(small_allowed.data(), allowed, allowed_length * sizeof(int));
        std::sort(small_allowed.begin(), small_allowed.begin() + allowed_length);
        auto last = std::unique(small_allowed.begin(), small_allowed.begin() + allowed_length);
        allowed_length = std::distance(small_allowed.begin(), last);
    } else {
        std::vector<int> allowed_copy(allowed, allowed + allowed_length);
        std::sort(allowed_copy.begin(), allowed_copy.end());
        auto last = std::unique(allowed_copy.begin(), allowed_copy.end());
        allowed_copy.erase(last, allowed_copy.end());
        const int* allowed_data = allowed_copy.data();
        size_t new_length = allowed_copy.size();

        size_t matches = 0;
        const int* query_end = queries + queries_length;

        for (const int* query = queries; query != query_end; ++query) {
            if (std::binary_search(allowed_data, allowed_data + new_length, *query)) {
                ++matches;
            }
        }
        return matches;
    }

    size_t matches = 0;
    const int* query_end = queries + queries_length;

    for (const int* query = queries; query != query_end; ++query) {
        if (use_small_array) {
            if (std::binary_search(small_allowed.begin(), small_allowed.begin() + allowed_length, *query)) {
                ++matches;
            }
        } else {
            if (std::binary_search(allowed, allowed + allowed_length, *query)) {
                ++matches;
            }
        }
    }

    return matches;
}

}
