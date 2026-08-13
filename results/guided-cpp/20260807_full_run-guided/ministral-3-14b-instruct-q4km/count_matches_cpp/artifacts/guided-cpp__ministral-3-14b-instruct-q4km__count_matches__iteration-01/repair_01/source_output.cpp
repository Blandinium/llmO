#include "library.h"
#include <algorithm>
#include <cstddef>
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

    // Early exit if no queries or no allowed values
    if (queries_length == 0 || allowed_length == 0) {
        return 0;
    }

    // Create a copy of allowed values to sort and unique
    std::vector<int> allowed_copy(allowed, allowed + allowed_length);
    std::sort(allowed_copy.begin(), allowed_copy.end());
    auto last = std::unique(allowed_copy.begin(), allowed_copy.end());
    allowed_copy.erase(last, allowed_copy.end());

    size_t matches = 0;
    const int* query_end = queries + queries_length;

    // Use binary search for O(log n) lookups in sorted allowed values
    for (const int* query = queries; query != query_end; ++query) {
        if (std::binary_search(allowed_copy.begin(), allowed_copy.end(), *query)) {
            ++matches;
        }
    }

    return matches;
}

}
