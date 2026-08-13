#include "library.h"
#include "sut_common.h"

#include <string>
#include <cstdio>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        // Pre-calculate the required buffer size
        size_t buffer_size = 2; // for "[]"
        for (size_t i = 0; i < input_length; ++i) {
            // Estimate space needed for each number (up to 20 digits for 64-bit int)
            // plus 2 characters for ", " (except first element)
            buffer_size += i > 0 ? 3 : 0;
            int num = input[i];
            if (num == 0) {
                buffer_size += 1;
            } else {
                int temp = num;
                if (temp < 0) {
                    buffer_size += 1; // for '-'
                    temp = -temp;
                }
                while (temp > 0) {
                    buffer_size += 1;
                    temp /= 10;
                }
            }
        }

        // Allocate buffer with exact size
        char* buffer = new char[buffer_size];
        char* ptr = buffer;

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
                if (num < 0) {
                    *ptr++ = '-';
                    num = -num;
                }
                char temp[20];
                char* tptr = temp + sizeof(temp) - 1;
                *tptr = '\0';
                while (num > 0) {
                    *--tptr = '0' + (num % 10);
                    num /= 10;
                }
                while (*tptr) {
                    *ptr++ = *tptr++;
                }
            }
        }

        // Write the closing bracket
        *ptr++ = ']';
        *ptr = '\0';

        return buffer;
    } catch (...) {
        return nullptr;
    }
}

}
