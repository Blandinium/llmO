#include "library.h"

#include <algorithm>
#include <cstdint>
#include <vector>

extern "C" {

int64_t repeated_sort(const int* input, size_t input_length, int rounds) {
    if (input == nullptr && input_length != 0) {
        return 0;
    }
    if (input_length == 0) {
        return 0;
    }

    try {
        std::vector<int> values(input, input + input_length);
        std::sort(values.begin(), values.end());

        const size_t n = values.size();
        const size_t mid = n / 2;
        const std::int64_t median = (n % 2 == 0)
            ? (static_cast<std::int64_t>(values[mid - 1]) + values[mid]) / 2
            : static_cast<std::int64_t>(values[mid]);

        std::int64_t total = 0;
        for (int r = 0; r < rounds; ++r) {
            total += median;
            total += values[r % n];
        }
        return total;
    } catch (...) {
        return 0;
    }
}

}
