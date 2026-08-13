#include "library.h"
#include <algorithm>
#include <numeric>
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

    // Use a bitmask for allowed values (assuming int is 32-bit)
    // This is only efficient if the range of allowed values is small
    const size_t max_int = static_cast<size_t>(1) << 31;
    std::vector<bool> allowed_mask(max_int, false);

    // Populate the allowed mask
    for (size_t i = 0; i < allowed_length; ++i) {
        if (allowed[i] >= 0 && static_cast<size_t>(allowed[i]) < max_int) {
            allowed_mask[static_cast<size_t>(allowed[i])] = true;
        }
    }

    // Count matches using a simple loop
    size_t matches = 0;
    for (size_t i = 0; i < queries_length; ++i) {
        if (queries[i] >= 0 && static_cast<size_t>(queries[i]) < max_int && 
            allowed_mask[static_cast<size_t>(queries[i])]) {
            ++matches;
        }
    }

    return matches;
}

}
