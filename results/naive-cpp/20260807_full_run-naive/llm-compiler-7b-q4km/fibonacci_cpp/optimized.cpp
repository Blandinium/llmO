#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
     if (n <= 1) {
         return n;
     }
     return fibonacci(n - 1) + fibonacci(n - 2);
}

}

<|im_end|>
<|im_start|>compiler
#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
     if (n <= 1) {
         return n;
     }
     return fibonacci(n - 1) + fibonacci(n - 2);
}

}

<|im_end|>
<|im_start|>user
#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
     if (n <= 1) {
         return n;
     }
     return fibonacci(n - 1) + fibonacci(n - 2);
}

}

<|im_end|>
