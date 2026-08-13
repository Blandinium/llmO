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
        size_t total_size = 2; // for "[]"
        for (size_t i = 0; i < input_length; ++i) {
            // Estimate size for each number (up to 20 digits for 64-bit int)
            // Plus 2 for ", " (except for the first element)
            total_size += i > 0 ? 3 : 0;
            int num = input[i];
            if (num == 0) {
                total_size += 1;
            } else {
                // Count digits
                int temp = num;
                if (temp < 0) temp = -temp;
                while (temp > 0) {
                    total_size++;
                    temp /= 10;
                }
            }
        }

        // Allocate the string buffer directly
        std::vector<char> buffer(total_size);
        char* ptr = buffer.data();

        // Write the opening bracket
        *ptr++ = '[';

        // Write each number
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                *ptr++ = ',';
                *ptr++ = ' ';
            }

            int num = input[i];
            if (num == 0) {
                *ptr++ = '0';
            } else {
                // Handle negative numbers
                if (num < 0) {
                    *ptr++ = '-';
                    num = -num;
                }

                // Convert digits
                char* start = ptr;
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

        // Null-terminate the string
        *ptr = '\0';

        // Copy to C string (copy_to_c_string will handle allocation)
        return copy_to_c_string(std::string(buffer.data(), ptr - buffer.data()));
    } catch (...) {
        return nullptr;
    }
}

}
