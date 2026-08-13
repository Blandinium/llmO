#include "library.h"
#include "sut_common.h"

#include <string>
#include <string_view>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        // Pre-allocate buffer with exact capacity
        std::string result;
        result.reserve(input_length * 12 + 2); // 12 chars per int (avg) + brackets

        result.push_back('[');
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                result.push_back(',');
                result.push_back(' ');
            }

            // Fast path for small numbers (most common case)
            int value = input[i];
            if (value >= -9 && value <= 9999) {
                // Use direct digit writing for small numbers
                char buffer[12];
                char* ptr = buffer + sizeof(buffer);
                *--ptr = '\0';

                if (value < 0) {
                    *--ptr = '-';
                    value = -value;
                }

                do {
                    *--ptr = '0' + (value % 10);
                    value /= 10;
                } while (value > 0);

                result.append(ptr, buffer + sizeof(buffer) - ptr);
            } else {
                result += std::to_string(value);
            }
        }
        result.push_back(']');

        return copy_to_c_string(result);
    } catch (...) {
        return nullptr;
    }
}

}
