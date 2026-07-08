#include "library.h"

#include <cstdlib>

extern "C" {

void free_string(char* value) {
    std::free(value);
}

void free_word_counts(WordCount* values, size_t length) {
    if (values == nullptr) {
        return;
    }

    for (size_t i = 0; i < length; ++i) {
        std::free(values[i].word);
    }

    std::free(values);
}

}
