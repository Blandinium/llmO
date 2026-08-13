#include "library.h"

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

    const bool allowed_null = (allowed == nullptr);
    const bool queries_null = (queries == nullptr);
    
    if (allowed_null || queries_null) {
        return 0;
    }

    const size_t allowed_size = allowed_length;
    const size_t queries_size = queries_length;
    
    if (allowed_size == 0 || queries_size == 0) {
        return 0;
    }

    const int* allowed_end = allowed + allowed_size;
    const int* queries_end = queries + queries_size;
    
    size_t matches = 0;
    
    for (const int* q = queries; q < queries_end; ++q) {
        const int value = *q;
        const int* a = allowed;
        const int* a_end = allowed_end;
        
        while (a < a_end) {
            if (*a == value) {
                ++matches;
                break;
            }
            ++a;
        }
    }
    
    return matches;
}

}
