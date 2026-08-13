#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
    uint64_t a = 0, b = 1;
    while (n-- > 1) {
        uint64_t c = a + b;
        a = b;
        b = c;
    }
    return b;
}

}
