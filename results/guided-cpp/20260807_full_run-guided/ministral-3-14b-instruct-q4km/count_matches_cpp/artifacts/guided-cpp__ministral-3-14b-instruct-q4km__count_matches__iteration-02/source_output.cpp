#include "library.h"
#include <algorithm>
#include <cstddef>
#include <cstring>

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

    // Allocate a single buffer for both sorting and searching
    int* allowed_sorted = new int[allowed_length];
    std::memcpy(allowed_sorted, allowed, allowed_length * sizeof(int));

    // Sort and remove duplicates in-place
    std::sort(allowed_sorted, allowed_sorted + allowed_length);
    size_t unique_count = std::unique(allowed_sorted, allowed_sorted + allowed_length) - allowed_sorted;

    size_t matches = 0;
    const int* query_end = queries + queries_length;

    // Use binary search for O(log n) lookups
    for (const int* query = queries; query != query_end; ++query) {
        if (std::binary_search(allowed_sorted, allowed_sorted + unique_count, *query)) {
            ++matches;
        }
    }

    delete[] allowed_sorted;
    return matches;
}

}
