#include "library.h"
#include "sut_common.h"

#include <string>
#include <string_view>
#include <charconv>
#include <cstdint>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        // Pre-calculate total required capacity to minimize reallocations
        size_t total_length = 2 + input_length * 2; // "[", "]" and ", " separators
        for (size_t i = 0; i < input_length; ++i) {
            int value = input[i];
            total_length += (value < 0) ? 12 : 11; // "-2147483648" vs "2147483647"
        }

        std::string result;
        result.reserve(total_length);

        result += '[';
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                result += ", ";
            }

            int value = input[i];
            char buffer[32];
            auto [ptr, ec] = std::to_chars(buffer, buffer + sizeof(buffer), value);
            result.append(buffer, ptr);
        }
        result += ']';

        return copy_to_c_string(result);
    } catch (...) {
        return nullptr;
    }
}

}
