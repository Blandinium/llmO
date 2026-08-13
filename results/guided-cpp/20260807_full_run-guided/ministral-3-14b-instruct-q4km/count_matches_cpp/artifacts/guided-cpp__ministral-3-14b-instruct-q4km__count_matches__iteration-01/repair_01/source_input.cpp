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

    // Early exit if no queries or no allowed values
    if (queries_length == 0 || allowed_length == 0) {
        return 0;
    }

    // Sort and unique the allowed values for faster lookup
    const int* allowed_end = allowed + allowed_length;
    std::sort(allowed, allowed_end);
    const int* last = std::unique(allowed, allowed_end);
    allowed_length = last - allowed;

    size_t matches = 0;
    const int* query_end = queries + queries_length;

    // Use binary search for O(log n) lookups in sorted allowed values
    for (const int* query = queries; query != query_end; ++query) {
        if (std::binary_search(allowed, allowed + allowed_length, *query)) {
            ++matches;
        }
    }

    return matches;
}

}
