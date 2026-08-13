#include "library.h"
#include "sut_common.h"

#include <string>

extern "C" {

char* format_list(const int* input, size_t input_length) {
    if (input == nullptr && input_length != 0) {
        return nullptr;
    }

    try {
        std::string result = "[";
        for (size_t i = 0; i < input_length; ++i) {
            if (i > 0) result += ", ";
            result += std::to_string(input[i]);
        }
        result += "]";

        return copy_to_c_string(result);
    } catch (...) {
        return nullptr;
    }
}

}
