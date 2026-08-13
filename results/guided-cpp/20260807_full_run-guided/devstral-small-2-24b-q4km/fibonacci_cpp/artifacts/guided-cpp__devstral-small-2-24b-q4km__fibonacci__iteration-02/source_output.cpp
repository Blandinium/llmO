#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
    if (n <= 1) {
        return n;
    }

    uint64_t a = 0;
    uint64_t b = 1;
    uint64_t c;

    // Use a larger unroll factor to reduce loop overhead
    const uint64_t unroll = 8;
    uint64_t i = 2;

    // Process 8 iterations at a time
    for (; i + unroll - 1 <= n; i += unroll) {
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
        c = a + b; a = b; b = c;
    }

    // Process remaining iterations
    for (; i <= n; ++i) {
        c = a + b;
        a = b;
        b = c;
    }

    return b;
}

}
