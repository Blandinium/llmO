#include "library.h"
#include "sut_common.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
     if (n <= 1) {
         return n;
     }
     return fibonacci(n - 1) + fibonacci(n - 2);
}

}
