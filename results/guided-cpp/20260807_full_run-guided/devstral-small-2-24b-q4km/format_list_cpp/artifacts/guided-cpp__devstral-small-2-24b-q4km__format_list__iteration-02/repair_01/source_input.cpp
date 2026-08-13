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
        // Pre-calculate the total size needed for the output string
        size_t total_size = 2; // for '[' and ']'
        for (size_t i = 0; i < input_length; ++i) {
            // Estimate the number of digits in each number (plus comma and space)
            int num = input[i];
            size_t digits = (num == 0) ? 1 : (size_t)log10(abs(num)) + 1;
            total_size += digits + (i > 0 ? 2 : 0); // +2 for ", "
        }

        // Allocate the buffer directly
        std::vector<char> buffer(total_size);
        char* ptr = buffer.data();

        // Write the opening bracket
        *ptr++ = '[';

        // Write each number with comma separator
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                *ptr++ = ',';
                *ptr++ = ' ';
            }

            // Convert number to string directly into buffer
            int num = input[i];
            if (num == 0) {
                *ptr++ = '0';
            } else {
                char* start = ptr;
                if (num < 0) {
                    *ptr++ = '-';
                    num = -num;
                }
                while (num > 0) {
                    *ptr++ = '0' + (num % 10);
                    num /= 10;
                }
                // Reverse the digits
                std::reverse(start, ptr);
            }
        }

        // Write the closing bracket
        *ptr++ = ']';
        *ptr = '\0';

        // Copy to C string (copy_to_c_string will handle allocation)
        return copy_to_c_string(std::string(buffer.data(), ptr - buffer.data()));
    } catch (...) {
        return nullptr;
    }
}

}
