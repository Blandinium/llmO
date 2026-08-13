#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
    if (n <= 1) {
        return n;
    }
    
    uint64_t a = 0;
    uint64_t b = 1;
    // Use a larger step size to reduce loop iterations
    for (uint64_t i = 2; i <= n; i += 2) {
        uint64_t c = a + b;
        a = b;
        b = c;
        
        // Process the next iteration if needed
        if (i + 1 <= n) {
            uint64_t d = a + b;
            a = b;
            b = d;
        }
    }
    return b;
}

}
