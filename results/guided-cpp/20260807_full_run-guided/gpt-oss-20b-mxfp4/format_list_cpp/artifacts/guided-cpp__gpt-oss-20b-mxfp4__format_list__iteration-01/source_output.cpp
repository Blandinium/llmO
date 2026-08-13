#include "library.h"
#include "sut_common.h"

#include <cstdlib>
#include <charconv>
#include <cstddef>
#include <cstdint>

extern "C" {

static inline size_t int_decimal_length(int value) {
    // Compute the number of characters needed to represent an int in decimal.
    // Use a small buffer and std::to_chars to avoid branching.
    char tmp[12]; // enough for 32-bit int including sign
    auto result = std::to_chars(tmp, tmp + sizeof(tmp), value);
    return static_cast<size_t>(result.ptr - tmp);
}

char* format_list(const int* input, size_t input_length) {
    // Handle invalid input pointer.
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    // Compute total length: '[' + numbers + ', ' separators + ']' + '\0'
    size_t total_len = 2; // '[' and ']'
    for (size_t i = 0; i < input_length; ++i) {
        if (i > 0) {
            total_len += 2; // ", "
        }
        total_len += int_decimal_length(input[i]);
    }

    // Allocate buffer
    char* buffer = static_cast<char*>(std::malloc(total_len + 1));
    if (!buffer) {
        return nullptr;
    }

    char* p = buffer;
    *p++ = '[';
    for (size_t i = 0; i < input_length; ++i) {
        if (i > 0) {
            *p++ = ',';
            *p++ = ' ';
        }
        // Convert integer to decimal string
        char tmp[12];
        auto result = std::to_chars(tmp, tmp + sizeof(tmp), input[i]);
        size_t len = static_cast<size_t>(result.ptr - tmp);
        std::memcpy(p, tmp, len);
        p += len;
    }
    *p++ = ']';
    *p = '\0';

    return buffer;
}

}
