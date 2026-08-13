#include "library.h"
#include <unordered_set>

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

    // Create a lookup set for O(1) lookups
    const size_t allowed_size = allowed_length;
    const int* allowed_data = allowed;
    
    // Use a hash set for allowed values
    std::unordered_set<int> allowed_set(allowed_data, allowed_data + allowed_length);
    
    // Count matches
    size_t matches = 0;
    for (size_t i = 0; i < queries_length; ++i) {
        if (allowed_set.count(queries[i])) {
            ++matches;
        }
    }
    
    return matches;
}

}
