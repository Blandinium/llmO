#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
    if (n <= 1) {
        return n;
    }

    // Fast doubling algorithm: compute (F(n), F(n+1)) iteratively.
    uint64_t a = 0; // F(0)
    uint64_t b = 1; // F(1)

    // Find the position of the most significant bit of n.
    int msb = 63 - __builtin_clzll(n);

    for (int i = msb; i >= 0; --i) {
        // Compute:
        //   c = F(2k)   = F(k) * [2*F(k+1) – F(k)]
        //   d = F(2k+1) = F(k)^2 + F(k+1)^2
        unsigned __int128 t1 = (unsigned __int128)a * ((unsigned __int128)(2 * b - a));
        unsigned __int128 t2 = (unsigned __int128)a * a + (unsigned __int128)b * b;

        a = (uint64_t)t1; // F(2k)
        b = (uint64_t)t2; // F(2k+1)

        // If the current bit of n is set, advance one step:
        //   F(2k+1) becomes F(2k+2) = F(2k) + F(2k+1)
        if ((n >> i) & 1ULL) {
            unsigned __int128 t3 = (unsigned __int128)a + b;
            a = b;
            b = (uint64_t)t3;
        }
    }

    return a; // F(n)
}

}
