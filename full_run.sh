#!/usr/bin/env bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <run-id>" >&2
    exit 2
fi

run_id=$1
if [[ ! $run_id =~ ^[a-z0-9][a-z0-9_-]*$ ]]; then
    echo "Error: run-id must start with a lowercase letter or digit and contain only lowercase letters, digits, underscores, and hyphens." >&2
    exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
cd -- "$script_dir"

llvm_run_id="${run_id}-llvm"
naive_run_id="${run_id}-naive"
guided_run_id="${run_id}-guided"
ir_run_id="${run_id}-ir"
extracted_ir_run_id="${run_id}-extracted-ir"
matrix_run_id="${run_id}-matrix"

./run_builds.py --run-id "$llvm_run_id"
./run_naive_cpp_optimization.py --run-id "$naive_run_id"
./run_iterative_cpp_optimization.py --run-id "$guided_run_id"
./run_ir_optimization.py --run-id "$ir_run_id" --backend-opt-level both
./run_ir_optimization.py --mode extracted-ir --run-id "$extracted_ir_run_id" --backend-opt-level both

./run_final_benchmark_matrix.py \
    --run-id "$matrix_run_id" \
    --source-run "results/llvm/$llvm_run_id" \
    --source-run "results/naive-cpp/$naive_run_id" \
    --source-run "results/guided-cpp/$guided_run_id" \
    --source-run "results/llm-ir/$ir_run_id" \
    --source-run "results/extracted-ir/$extracted_ir_run_id"

echo "Definitive matrix written to results/final-matrix/$matrix_run_id/summary.json"
