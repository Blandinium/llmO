#include "library.h"
#include "sut_common.h"

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    // Pre-allocate buffer with maximum possible size
    size_t buffer_size = 1; // [
    for (size_t i = 0; i < input_length; ++i) {
        // Each integer can be up to 20 digits (for 64-bit integers)
        // Plus commas, spaces, and brackets
        buffer_size += 20 + 2 + 1; // 20 digits + ", " + 1 for safety
    }
    buffer_size += 1; // ]

    char* buffer = static_cast<char*>(malloc(buffer_size));
    if (!buffer) return nullptr;

    char* ptr = buffer;
    *ptr++ = '[';

    for (size_t i = 0; i < input_length; ++i) {
        if (i > 0) {
            *ptr++ = ',';
            *ptr++ = ' ';
        }

        // Convert integer to string manually
        char num_buffer[20];
        size_t num_len = 0;
        int value = input[i];
        if (value < 0) {
            *ptr++ = '-';
            value = -value;
        }

        // Handle special case for 0
        if (value == 0) {
            *ptr++ = '0';
            continue;
        }

        // Convert to string manually
        char* num_ptr = num_buffer + sizeof(num_buffer);
        *--num_ptr = '\0';
        while (value > 0) {
            *--num_ptr = '0' + (value % 10);
            value /= 10;
        }

        num_len = num_buffer + sizeof(num_buffer) - num_ptr;
        memcpy(ptr, num_ptr, num_len);
        ptr += num_len;
    }

    *ptr++ = ']';
    *ptr = '\0';

    return buffer;
}

}
