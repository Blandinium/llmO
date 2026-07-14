#include "sut_common.h"

#include <cctype>
#include <cstdlib>
#include <cstring>
#include <string>

char* copy_to_c_string(const std::string& value) {
    char* copy = static_cast<char*>(std::malloc(value.size() + 1));
    if (copy == nullptr) {
        return nullptr;
    }

    std::memcpy(copy, value.c_str(), value.size() + 1);
    return copy;
}

bool is_word_char(char c) {
    return std::isalpha(static_cast<unsigned char>(c)) != 0;
}

char normalize_char(char c) {
    return static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
}
