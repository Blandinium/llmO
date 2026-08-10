import platform
import socket
import sys
import os
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from .config import (
    CLANG_CXX_COMPILER, LLVM_OPT_TOOL, LLVM_AS_TOOL, LLVM_EXTRACT_TOOL,
    LLVM_LINK_TOOL, LLAMA_SERVER_EXECUTABLE, PROJECT_ROOT,
)

def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"

def get_git_dirty() -> bool:
    try:
        status = subprocess.check_output(["git", "status", "--porcelain"], cwd=str(PROJECT_ROOT), text=True, stderr=subprocess.DEVNULL).strip()
        return len(status) > 0
    except Exception:
        return False

def get_tool_version(tool: str) -> str:
    try:
        return subprocess.check_output([tool, "--version"], text=True, stderr=subprocess.DEVNULL).splitlines()[0].strip()
    except Exception:
        return "unknown"

def get_cpu_info() -> Dict[str, Any]:
    info = {
        "host_cpu": platform.processor() or "unknown",
        "cpu_architecture": platform.machine(),
        "logical_cpu_count": os.cpu_count(),
        "physical_core_count": None
    }
    
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        info["host_cpu"] = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass

        try:
            # Try lscpu for core counts if available
            lscpu = subprocess.check_output(["lscpu", "-p=Core,Socket"], text=True, stderr=subprocess.DEVNULL)
            cores = set()
            for line in lscpu.splitlines():
                if not line.startswith("#"):
                    cores.add(line.strip())
            info["physical_core_count"] = len(cores)
        except Exception:
            pass

    return info

def get_llama_server_version(executable: str) -> Dict[str, Any]:
    details = {
        "version": "unknown",
        "command_attempted": None,
        "returncode": None,
        "stdout": "",
        "stderr": ""
    }
    
    for flag in ["--version", "-version"]:
        try:
            details["command_attempted"] = f"{executable} {flag}"
            proc = subprocess.run([executable, flag], text=True, capture_output=True, timeout=5)
            details["returncode"] = proc.returncode
            details["stdout"] = proc.stdout
            details["stderr"] = proc.stderr
            
            output = (proc.stdout + proc.stderr).strip()
            if output:
                details["version"] = output.splitlines()[0].strip()
                break
        except Exception as e:
            details["stderr"] += f"\nError: {str(e)}"
            
    return details

def get_run_metadata() -> Dict[str, Any]:
    cpu_info = get_cpu_info()
    llama_version_info = get_llama_server_version(LLAMA_SERVER_EXECUTABLE)
    
    meta = {
        "start_time": datetime.now().isoformat(),
        "git_commit": get_git_commit(),
        "git_dirty": get_git_dirty(),
        "hostname": socket.gethostname(),
        "kernel": platform.release(),
        "python_version": sys.version,
        "clang_version": get_tool_version(CLANG_CXX_COMPILER),
        "opt_version": get_tool_version(LLVM_OPT_TOOL),
        "llvm_as_version": get_tool_version(LLVM_AS_TOOL),
        "llvm_extract_version": get_tool_version(LLVM_EXTRACT_TOOL),
        "llvm_link_version": get_tool_version(LLVM_LINK_TOOL),
        "llama_server_version": llama_version_info["version"],
        "llama_server_version_details": llama_version_info,
    }
    meta.update(cpu_info)
    return meta

def get_file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
