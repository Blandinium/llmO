#include "library.h"

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

        // Use a fixed-size buffer to avoid dynamic allocations
        std::vector<int> values(input, input + input_length);
        const size_t size = values.size();

        for (int r = 0; r < rounds; ++r) {
            // Sort the array in-place
            std::ranges::sort(values);

            const size_t mid = size / 2;
            const int median = (size % 2 == 0)
                ? static_cast<int>((static_cast<std::int64_t>(values[mid - 1]) + values[mid]) / 2)
                : values[mid];

            total += median;
            total += values[r % size];
        }

        return total;
    } catch (...) {
        return 0;
    }
}

}
