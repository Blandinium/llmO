#include "library.h"

#include <algorithm>

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

    if (allowed_length == 0) {
        return 0;
    }

    std::sort(const_cast<int*>(allowed), const_cast<int*>(allowed) + allowed_length);
    size_t matches = 0;

    for (size_t i = 0; i < queries_length; ++i) {
        const int query = queries[i];
        const int* first = allowed;
        const int* last = allowed + allowed_length;
        if (std::binary_search(first, last, query)) {
            ++matches;
        }
    }

    return matches;
}

}
