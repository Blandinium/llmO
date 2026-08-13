#include "library.h"
#include "sut_common.h"

#include <cstring>
#include <string>
#include <string_view>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    // Pre-calculate approximate buffer size to minimize reallocations
    size_t buffer_size = 2 + input_length * 12; // "[", "]", ", " and 10 chars per number on average
    char* buffer = static_cast<char*>(malloc(buffer_size));
    if (!buffer) return nullptr;

    char* pos = buffer;
    *pos++ = '[';

    for (size_t i = 0; i < input_length; ++i) {
        if (i > 0) {
            *pos++ = ',';
            *pos++ = ' ';
        }

        // Convert number directly to string in buffer
        int value = input[i];
        char* num_start = pos;
        char* num_end = pos;

        // Handle negative numbers
        if (value < 0) {
            *pos++ = '-';
            value = -value;
        }

        // Convert digits
        char digits[12];
        char* digit_pos = digits + sizeof(digits);
        *--digit_pos = '\0';

        do {
            *--digit_pos = '0' + (value % 10);
            value /= 10;
        } while (value > 0 && digit_pos > digits);

        // Copy digits to buffer
        size_t digit_count = digits + sizeof(digits) - digit_pos;
        std::memcpy(pos, digit_pos, digit_count);
        pos += digit_count;
    }

    *pos++ = ']';
    *pos = '\0';

    return buffer;
}

}
