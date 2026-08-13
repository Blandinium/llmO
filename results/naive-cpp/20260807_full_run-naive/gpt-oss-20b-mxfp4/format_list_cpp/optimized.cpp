#include "library.h"
#include "sut_common.h"

#include <string>
#include <charconv>
#include <cstddef>
#include <stdexcept>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        std::string result;
        // Rough estimate: '[' + ']' + each number up to 11 chars + ", " (2 chars) per element
        result.reserve(2 + input_length * 13);
        result.push_back('[');

        char buf[12]; // enough for 32-bit int including sign
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) {
                result.push_back(',');
                result.push_back(' ');
            }
            auto [ptr, ec] = std::to_chars(buf, buf + sizeof(buf), input[i]);
            if (ec != std::errc()) {
                return nullptr;
            }
            result.append(buf, ptr);
        }

        result.push_back(']');
        return copy_to_c_string(result);
    } catch (...) {
        return nullptr;
    }
}

}
