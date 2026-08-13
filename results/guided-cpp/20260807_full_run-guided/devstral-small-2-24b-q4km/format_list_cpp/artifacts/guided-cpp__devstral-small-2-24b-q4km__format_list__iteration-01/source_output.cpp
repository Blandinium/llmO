#include "library.h"
#include "sut_common.h"

#include <string>
#include <vector>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        // Pre-calculate the total length needed
        size_t total_length = 2; // for '[' and ']'
        for (size_t i = 0; i < input_length; ++i) {
            // Estimate length for each number (max 20 digits for 64-bit int)
            total_length += 20;
            if (i > 0) total_length += 2; // for ", "
        }

        // Allocate buffer directly
        std::vector<char> buffer(total_length);
        char* ptr = buffer.data();

        // Write the list
        *ptr++ = '[';
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                *ptr++ = ',';
                *ptr++ = ' ';
            }
            ptr += std::snprintf(ptr, total_length - (ptr - buffer.data()), "%d", input[i]);
        }
        *ptr++ = ']';
        *ptr = '\0';

        // Copy to C string (copy_to_c_string will handle allocation)
        return copy_to_c_string(std::string(buffer.data(), ptr - buffer.data()));
    } catch (...) {
        return nullptr;
    }
}

}
