#include "library.h"
#include "sut_common.h"

#include <string>
#include <string_view>
#include <charconv>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        // Precompute total length to minimize reallocations
        size_t total_length = 2; // For '[]'
        for (size_t i = 0; i < input_length; ++i) {
            int value = input[i];
            size_t num_digits = (value < 0) ? 1 : 0;
            int temp = value;
            while (temp) {
                temp /= 10;
                num_digits++;
            }
            total_length += num_digits + (i > 0 ? 2 : 0); // +2 for ", "
        }

        std::string result;
        result.reserve(total_length);
        result.push_back('[');

        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                result.push_back(',');
                result.push_back(' ');
            }

            int value = input[i];
            char buffer[32];
            auto [ptr, ec] = std::to_chars(buffer, buffer + sizeof(buffer), value);
            result.append(buffer, ptr);
        }

        result.push_back(']');
        return copy_to_c_string(result);
    } catch (...) {
        return nullptr;
    }
}

}
