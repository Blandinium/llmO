#include "library.h"
#include <algorithm>
#include <vector>
#include <cstdint>
#include <array>

extern "C" {

int64_t repeated_sort(const int* input, size_t input_length, int rounds) {
    if (input == nullptr && input_length != 0) {
        return 0;
    }

    if (input_length == 0) {
        return 0;
    }

    std::int64_t total = 0;
    std::array<int, 16> buffer;

    // Handle small arrays directly in buffer to avoid allocations
    if (input_length <= buffer.size()) {
        for (int r = 0; r < rounds; ++r) {
            std::copy(input, input + input_length, buffer.begin());
            std::ranges::sort(buffer.begin(), buffer.begin() + input_length);

            const size_t mid = input_length / 2;
            const int median = (input_length % 2 == 0)
                ? static_cast<int>((static_cast<std::int64_t>(buffer[mid - 1]) + buffer[mid]) / 2)
                : buffer[mid];

            total += median;
            total += buffer[r % input_length];
        }
        return total;
    }

    // For larger arrays, use a single allocation that persists across rounds
    std::vector<int> values(input, input + input_length);

    for (int r = 0; r < rounds; ++r) {
        std::ranges::sort(values.begin(), values.end());

        const size_t mid = values.size() / 2;
        const int median = (values.size() % 2 == 0)
            ? static_cast<int>((static_cast<std::int64_t>(values[mid - 1]) + values[mid]) / 2)
            : values[mid];

        total += median;
        total += values[r % values.size()];
    }

    return total;
}

}
