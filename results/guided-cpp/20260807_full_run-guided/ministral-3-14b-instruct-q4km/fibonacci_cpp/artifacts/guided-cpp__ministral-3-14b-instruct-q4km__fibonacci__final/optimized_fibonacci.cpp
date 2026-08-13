#include "library.h"

extern "C" {
    uint64_t fibonacci(uint64_t n) {
        if (n <= 1) return n;

        uint64_t a = 0;
        uint64_t b = 1;
        uint64_t c = 0;

        // Use unsigned comparison to avoid branch mispredictions
        for (uint64_t i = 2; ; ++i) {
            c = a + b;
            a = b;
            b = c;

            // Early exit when we've computed enough iterations
            if (i == n) break;
        }
        return b;
    }
}
