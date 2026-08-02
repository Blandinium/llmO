import sys
import os
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from run_ir_optimization import main
from llmo.config import PROJECT_ROOT, SUT_DIR

def mock_call_llm(model_name, prompt, system_prompt=None, max_tokens=None, seed=None):
    # Extract IR from prompt (it's the last part after "Input IR:")
    ir_start = prompt.find("Input IR:")
    if ir_start != -1:
        ir_content = prompt[ir_start + len("Input IR:"):].strip()
    else:
        ir_content = "; empty"
        
    from llmo.llama import ChatCompletionResult
    return ChatCompletionResult(
        content=ir_content,
        finish_reason="stop",
        prompt_tokens=100,
        completion_tokens=100,
        total_tokens=200,
        raw_response={"mock": True}
    )

def mock_run_command(command, cwd, stdout_file, stderr_file, env=None, timeout_seconds=None):
    from llmo.command import CommandResult
    # Mock successful execution
    
    # If it's the IR generation command, create the output file
    if "-emit-llvm" in command:
        output_file = Path(command[command.index("-o") + 1])
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("target triple = \"x86_64-unknown-linux-gnu\"\ntarget datalayout = \"e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128\"\ndefine i64 @fibonacci(i64 %n) {\nret i32 0\n}")
    elif "-S" in command and "-o" in command:
         output_file = Path(command[command.index("-o") + 1])
         output_file.parent.mkdir(parents=True, exist_ok=True)
         output_file.write_text("target triple = \"x86_64-unknown-linux-gnu\"\ntarget datalayout = \"e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128\"\ndefine i64 @fibonacci(i64 %n) {\nret i32 0\n}")
    elif "-shared" in command and "-o" in command:
         output_file = Path(command[command.index("-o") + 1])
         output_file.parent.mkdir(parents=True, exist_ok=True)
         output_file.write_text("mock lib")
    
    if "nm" in command:
        # Mock nm output for all required symbols
        from llmo.config import REQUIRED_ABI_SYMBOLS
        nm_output = "\n".join([f"0000000000000000 T {s}" for s in REQUIRED_ABI_SYMBOLS])
        Path(stdout_file).write_text(nm_output)
    else:
        Path(stdout_file).write_text("{\"calls_per_second\": 1000.0, \"wall_time_s\": 1.0}")
    
    Path(stderr_file).write_text("")
    return CommandResult(command, str(cwd), 0, 0.1, str(stdout_file), str(stderr_file))

@patch("run_ir_optimization.start_llama_server", return_value=(MagicMock(), ["mock-server"]))
@patch("run_ir_optimization.wait_for_llama_ready")
@patch("run_ir_optimization.warm_up_llm")
@patch("run_ir_optimization.call_llm", side_effect=mock_call_llm)
@patch("llmo.llama.http_json")
@patch("llmo.llvm.run_command", side_effect=mock_run_command)
@patch("llmo.benchmark.run_command", side_effect=mock_run_command)
@patch("llmo.abi.run_command", side_effect=mock_run_command)
def test_smoke_ir(mock_abi, mock_bench, mock_llvm, mock_http, mock_call, mock_warm, mock_ready, mock_start):
    # Set up arguments
    test_output = PROJECT_ROOT / "smoke-test-ir-out"
    if test_output.exists():
        shutil.rmtree(test_output)
    
    sys.argv = [
        "run_ir_optimization.py",
        "--only", "fibonacci",
        "--model", "qwen3-14b-q4km",
        "--output-root", str(test_output),
        "--backend-opt-level", "both",
        "--benchmark-repetitions", "1",
        "--run-id", "smoke-test"
    ]
    
    # Mock EFFECTIVE_LLAMA_CTX_SIZE
    import llmo.llama
    llmo.llama.EFFECTIVE_LLAMA_CTX_SIZE = 32768
    
    main()
    
    # Verify results
    assert test_output.exists()
    summary_file = test_output / "smoke-test" / "qwen3_14b_q4km" / "fibonacci_cpp" / "summary.json"
    assert summary_file.exists()
    
    summary = json.loads(summary_file.read_text())
    assert summary["status"] == "completed"
    assert "-O0" in summary["backend_results"]
    assert "-O3" in summary["backend_results"]
    assert summary["backend_results"]["-O0"]["performance"] == "unchanged_within_noise"

if __name__ == "__main__":
    test_smoke_ir()
    print("Smoke test passed!")
