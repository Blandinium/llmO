#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
    uint64_t a = 0; // F(0)
    uint64_t b = 1; // F(1)
    for (int i = 63; i >= 0; --i) {
        // Compute F(2k) and F(2k+1) from F(k)=a, F(k+1)=b
        uint64_t t1 = a * ((b << 1) - a); // F(2k)
        uint64_t t2 = a * a + b * b;       // F(2k+1)
        if ((n >> i) & 1ULL) {
            a = t2;
            b = t1 + t2;
        } else {
            a = t1;
            b = t2;
        }
    }
    return a;
}

}
