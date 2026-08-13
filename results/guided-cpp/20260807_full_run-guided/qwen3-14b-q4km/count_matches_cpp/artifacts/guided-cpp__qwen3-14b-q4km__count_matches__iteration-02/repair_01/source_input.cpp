#include "library.h"
#include <algorithm>
#include <cstddef>

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

    // Use a bitmask for allowed values (assuming int is 32-bit)
    // This is only efficient if the range of allowed values is small
    const size_t max_int = static_cast<size_t>(1) << 31;
    if (allowed_length > max_int / sizeof(size_t)) {
        // Fallback to hash set if the range is too large
        std::unordered_set<int> allowed_set(allowed, allowed + allowed_length);
        size_t matches = 0;
        for (size_t i = 0; i < queries_length; ++i) {
            if (allowed_set.count(queries[i])) {
                ++matches;
            }
        }
        return matches;
    }

    // Create a bitmask for allowed values
    size_t allowed_mask = 0;
    for (size_t i = 0; i < allowed_length; ++i) {
        allowed_mask |= static_cast<size_t>(1) << (allowed[i] & 0x1F);
    }

    // Count matches using bitmask
    size_t matches = 0;
    for (size_t i = 0; i < queries_length; ++i) {
        if ((allowed_mask & (static_cast<size_t>(1) << (queries[i] & 0x1F))) != 0) {
            ++matches;
        }
    }

    return matches;
}

}
