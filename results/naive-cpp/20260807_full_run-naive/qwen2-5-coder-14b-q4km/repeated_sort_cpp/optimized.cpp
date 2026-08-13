#include "library.h"

#include <algorithm>
#include <cstdint>
#include <vector>

extern "C" {

int64_t repeated_sort(const int* input, size_t input_length, int rounds) {
    if (input == nullptr && input_length != 0) {
        return 0;
    }

    try {
        if (input_length == 0) {
            return 0;
        }

        std::int64_t total = 0;

        // Pre-allocate vector to avoid multiple allocations
        std::vector<int> values(input_length);
        std::copy(input, input + input_length, values.begin());

        for (int r = 0; r < rounds; ++r) {
            std::ranges::sort(values);

            const size_t mid = values.size() / 2;
            const int median = (values.size() % 2 == 0)
                ? static_cast<int>((static_cast<std::int64_t>(values[mid - 1]) + values[mid]) / 2)
                : values[mid];

            total += median;
            total += values[r % values.size()];
        }

        return total;
    } catch (...) {
        return 0;
    }
}

}
