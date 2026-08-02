You are an expert C++23 performance engineer.

You are iteratively optimizing fibonacci.cpp.
Optimization iteration 1 of 3

The current implementation compiles successfully and preserves the required ABI.

Clang was run at -O3 and emitted the optimization remarks below. These remarks describe optimizations Clang performed, missed, or analyzed.

Use them as diagnostic evidence to identify C++-level changes that could enable better generated code or improve the algorithm beyond what the compiler can do automatically.

Do not blindly follow every remark. Some remarks only explain a compiler decision and changing the source may not be beneficial.

Hard requirements:
- Return one complete replacement for fibonacci.cpp.
- Preserve the public C ABI exactly as declared in library.h.
- Do not change exported names, parameter types, return types, struct layouts, ownership rules, or allocation/free conventions.
- Do not implement unrelated exported functions.
- Preserve externally observable behavior for all valid inputs.
- Do not modify library.h or sut_common.h.
- Return raw C++ only.
- No Markdown, explanation, notes, or code fences.

Headers:
// library.h
#ifndef SUT_LIBRARY_H
#define SUT_LIBRARY_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct WordCount {
     char* word;
     uint64_t count;
} WordCount;

uint64_t fibonacci(uint64_t n);
char* format_list(const int* input, size_t input_length);
int64_t repeated_sort(const int* input, size_t input_length, int rounds);
size_t count_matches(
     const int* allowed,
     size_t allowed_length,
     const int* queries,
     size_t queries_length
);
WordCount* top_words_from_file(
     const char* path,
     const char* const* ignore_words,
     size_t ignore_words_length,
     size_t max_results,
     size_t* result_length
);
void free_string(char* value);
void free_word_counts(WordCount* values, size_t length);

#ifdef __cplusplus
}
#endif

#endif // SUT_LIBRARY_H


// sut_common.h
#ifndef SUT_COMMON_H
#define SUT_COMMON_H

#include <string>

char* copy_to_c_string(const std::string& value);
bool is_word_char(char c);
char normalize_char(char c);

#endif // SUT_COMMON_H


Current fibonacci.cpp:
#include "library.h"

extern "C" {

uint64_t fibonacci(uint64_t n) {
      if (n <= 1) {
         return n;
      }
     return fibonacci(n - 1) + fibonacci(n - 2);
}

}


Clang optimization remarks:
!Missed
Pass:            inline
Name:            NeverInline
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 12 }
Function:         fibonacci
Args:
   - String:          ''''
   - Callee:           fibonacci
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 5, Column: 0 }
   - String:          ''' not inlined into '''
   - Caller:           fibonacci
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 5, Column: 0 }
   - String:          ''' because it should never be inlined '
   - String:          '(cost=never)'
   - String:          ': '
   - Reason:          recursive
...
---
!Missed
Pass:            inline
Name:            NeverInline
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 31 }
Function:         fibonacci
Args:
   - String:          ''''
   - Callee:           fibonacci
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 5, Column: 0 }
   - String:          ''' not inlined into '''
   - Caller:           fibonacci
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 5, Column: 0 }
   - String:          ''' because it should never be inlined '
   - String:          '(cost=never)'
   - String:          ': '
   - Reason:          recursive
...
---
!Missed
Pass:            loop-vectorize
Name:            MissedDetails
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 6, Column: 11 }
Function:         fibonacci
Args:
   - String:          loop not vectorized
...
---
!Missed
Pass:            regalloc
Name:            SpillReloadCopies
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 5, Column: 1 }
Function:         fibonacci
Args:
   - NumVRCopies:       '2'
   - String:          ' virtual registers copies '
   - TotalCopiesCost: '2.000000e+00'
   - String:          ' total copies cost '
   - String:          generated in function
...
---
!Missed
Pass:            slp-vectorizer
Name:            NotBeneficial
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 12 }
Function:         fibonacci
Args:
   - String:          'List vectorization was possible but not beneficial with cost '
   - Cost:              '0'
   - String:          ' >= '
   - Treshold:         '0'
...
---
!Missed
Pass:            slp-vectorizer
Name:            NotBeneficial
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 12 }
Function:         fibonacci
Args:
   - String:          'List vectorization was possible but not beneficial with cost '
   - Cost:              '0'
   - String:          ' >= '
   - Treshold:         '0'
...
---
!Missed
Pass:            slp-vectorizer
Name:            NotBeneficial
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 12 }
Function:         fibonacci
Args:
   - String:          'List vectorization was possible but not beneficial with cost '
   - Cost:              '0'
   - String:          ' >= '
   - Treshold:         '0'
...
---
!Analysis
Pass:            loop-vectorize
Name:            CantVectorizeLibcall
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 12 }
Function:         fibonacci
Args:
   - String:          'loop not vectorized: '
   - String:          call instruction cannot be vectorized
...
---
!Analysis
Pass:            prologepilog
Name:            StackSize
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 5, Column: 0 }
Function:         fibonacci
Args:
   - NumStackBytes:   '24'
   - String:          ' stack bytes in function '''
   - Function:         fibonacci
   - String:          ''''
...
---
!Analysis
Pass:            asm-printer
Name:            InstructionMix
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 24 }
Function:         fibonacci
Args:
   - String:          'BasicBlock: '
   - BasicBlock:       ''
   - String:          "\n"
   - String:          ADD64ri32
   - String:          ': '
   - INST_ADD64ri32:   '1'
   - String:          "\n"
   - String:          ADD64rr
   - String:          ': '
   - INST_ADD64rr:      '1'
   - String:          "\n"
   - String:          CALL64pcrel32
   - String:          ': '
   - INST_CALL64pcrel32: '1'
   - String:          "\n"
   - String:          CMP64ri32
   - String:          ': '
   - INST_CMP64ri32:   '1'
   - String:          "\n"
   - String:          JCC_1
   - String:          ': '
   - INST_JCC_1:       '1'
   - String:          "\n"
   - String:          LEA64r
   - String:          ': '
   - INST_LEA64r:       '1'
   - String:          "\n"
...
---
!Analysis
Pass:            asm-printer
Name:            InstructionCount
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 5, Column: 0 }
Function:         fibonacci
Args:
   - NumInstructions: '19'
   - String:          ' instructions in function'
...
---
!Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:         fibonacci
Args:
   - String:          'BasicBlock: '
   - BasicBlock:       ''
   - String:          "\n"
   - String:          PUSH64r
   - String:          ': '
   - INST_PUSH64r:      '3'
   - String:          "\n"
   - String:          CMP64ri32
   - String:          ': '
   - INST_CMP64ri32:   '1'
   - String:          "\n"
   - String:          JCC_1
   - String:          ': '
   - INST_JCC_1:       '1'
   - String:          "\n"
   - String:          MOV64rr
   - String:          ': '
   - INST_MOV64rr:      '1'
   - String:          "\n"
   - String:          XOR32rr
   - String:          ': '
   - INST_XOR32rr:      '1'
   - String:          "\n"
...
---
!Analysis
Pass:            asm-printer
Name:            InstructionMix
Function:         fibonacci
Args:
   - String:          'BasicBlock: '
   - BasicBlock:       ''
   - String:          "\n"
   - String:          POP64r
   - String:          ': '
   - INST_POP64r:       '2'
   - String:          "\n"
   - String:          ADD64ri32
   - String:          ': '
   - INST_ADD64ri32:   '1'
   - String:          "\n"
   - String:          ADD64rr
   - String:          ': '
   - INST_ADD64rr:      '1'
   - String:          "\n"
   - String:          MOV64rr
   - String:          ': '
   - INST_MOV64rr:      '1'
   - String:          "\n"
   - String:          RET64
   - String:          ': '
   - INST_RET64:       '1'
   - String:          "\n"
...
---
!Passed
Pass:            tailcall-recursion
Name:            tailcall-recursion
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 9, Column: 31 }
Function:         fibonacci
Args:
   - String:          transforming tail recursion into loop
...
---
!Passed
Pass:            TTI
Name:            DontUnroll
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 6, Column: 11 }
Function:         fibonacci
Args:
   - String:          'advising against unrolling the loop because it contains a '
   - Call:             call
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 9, Column: 12 }
...
---
!Passed
Pass:            TTI
Name:            DontUnroll
DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                   Line: 6, Column: 11 }
Function:         fibonacci
Args:
   - String:          'advising against unrolling the loop because it contains a '
   - Call:             call
     DebugLoc:         { File: 'benchmark-builds/llm-cpp-remarks/llm_compiler_13b_q4km/fibonacci_cpp/baseline/fibonacci.cpp', 
                         Line: 9, Column: 12 }
...
<|im_end|>
<|im_start|>system
You are a compiler and C++ optimization assistant. Return only the requested source code.<|im_end|>
<|im_start|>user
You are an expert C++23 performance engineer.

You are iteratively optimizing fibon
