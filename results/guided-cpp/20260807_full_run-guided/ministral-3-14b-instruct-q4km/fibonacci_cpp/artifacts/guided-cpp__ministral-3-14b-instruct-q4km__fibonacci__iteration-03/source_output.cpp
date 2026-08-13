#include "library.h"

extern "C" {
    uint64_t fibonacci(uint64_t n) {
        if (n <= 1) return n;

        uint64_t a = 0;
        uint64_t b = 1;
        uint64_t c = 0;

        // Use unsigned comparison and unrolled loop with trip count
        // to minimize branch mispredictions and improve instruction level parallelism
        for (uint64_t i = 2; i <= n; i += 8) {
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;
            c = a + b; a = b; b = c;

            // Handle remaining iterations after unrolling
            if (i + 7 >= n) {
                for (uint64_t j = i + 8; j <= n; ++j) {
                    c = a + b; a = b; b = c;
                }
                break;
            }
        }
        return b;
    }
}
