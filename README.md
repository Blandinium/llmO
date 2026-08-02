# llmO

In his [keynote](https://accuonsea.uk/2026/sessions/the-next-20-weeks-of-systems-engineering/) at
ACCU on Sea 2026, Andrei Alexandrescu predicted LLMs would soon integrate with compilers for
better optimization. This repository contains benchmarks to test the usefullness of small, local
models today as part of the compiler optimization process.

## Requirements
- You'll need clang to compile the code (I used 20.1.8)
- The script expects llama.cpp for running the models (I built my own, based on the main branch of June 29 2026)
- Python is required to run the script which glues all pieces together
- Hardware that is capable of running the models you want to test with (If you are
patient, have sufficient RAM and a decent CPU, you don't need a GPU to run models). With some tweaks to the script,
it should be fairly easy to run the models elsewhere.

##  Results
The *benchmark-builds folders contain results from some of my runs. The .ll files in
20260712manual were not generated on local models, but on commercial AI agents.

## Structure
There are 5 files being benchmarked:
SUT/count_matches.cpp  SUT/fibonacci.cpp  SUT/format_list.cpp  SUT/repeated_sort.cpp and
SUT/top_words_from_file.cpp. I tried to create files with possible optimizaitons that are visible to
an experienced developper, but might not be easy to spot for a compiler.

These files are built into libSUT.so.

The librunner folder contains an application that will load libSUT.so, run tests to validate the
correctness of the 5 test methods, will try to calibrate how many iterations it needs to run
to run for roughly 30 seconds, and wil then run these iterations, and report how many iterations/s
were acchieved. This allows us to compare the performance of different versions of libSUT.so.

The run_builds.py will generate and benchmark builds for:
- Multiple LLVM optimizer flags ("-O0", "-O1", "-O2", "-O3", "-Ofast", "-Os", "-Oz")
- The C++ code optimized by diffirent local models
- The LLVM IR code, generated from the cpp test files, and optimized by local LLMs

LLVM IR is the language on which the compiler runs the optimizations. These measurements are
the results that matter to determine the usefullness of the current local models in the
optimization process.

## Usage

### LLVM IR Optimization Runner
This experiment measures the quality of LLVM IR transformations emitted by the LLM. It supports two backend pipelines for every candidate:
- **Direct IR Mode (-O0)**: Compiles the modified IR without further LLVM optimizations to isolate the LLM's contribution.
- **LLM plus LLVM Mode (-O3)**: Compiles the modified IR with full LLVM optimizations to see if the LLM transformation aids the conventional optimizer.

Run one model and one benchmark:
```bash
./run_ir_optimization.py --model qwen3-14b-q4km --only fibonacci --backend-opt-level both --benchmark-repetitions 1
```

Full run for the specialized LLM-compiler models:
```bash
./run_ir_optimization.py --model llm-compiler-7b-q4km --model llm-compiler-13b-q4km --benchmark-repetitions 3
```

### Naïve C++ Optimization Runner
Single-shot C++ optimization without feedback.
```bash
./run_naive_cpp_optimization.py --model qwen3-14b-q4km --only fibonacci
```

### Iterative C++ Optimization Runner
Feedback-driven optimization using compiler remarks.
```bash
./run_iterative_cpp_optimization.py --model qwen3-14b-q4km --only fibonacci
```

### Resuming an Interrupted Run
Use the `--resume` flag to skip already completed artifacts (those that reached a terminal status in all requested backend modes):
```bash
./run_ir_optimization.py --resume
```

### Unique Run Directories
Each run now creates a unique timestamped directory under the output root. You can specify a custom ID with:
```bash
./run_ir_optimization.py --run-id my-special-experiment
```

## Models
I've been testing with some models of simmilar size:
- gemma-4-12b
- qwen2.5-coder-14b
- qwen3-14b
- llm-compiler-13b

And with the smaller:
- llm-compiler-7b

## Conclusions?
This is a work in progress. I hope to share my conclusions soon
