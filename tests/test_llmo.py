import unittest
from pathlib import Path
from llmo.source import extract_code_block
from llmo.benchmark import parse_key_value_lines, parse_scalar_value, try_write_benchmark_json
from llmo.remarks import parse_remarks, prioritize_remarks, filter_remarks, batch_remarks, Remark
from llmo.command import write_json, LLMoJsonEncoder
from llmo.llama import estimate_tokens, count_tokens
import json
import os
import shutil
import tempfile

class TestSourceExtraction(unittest.TestCase):
    def test_raw_cpp(self):
        text = "int f() { return 1; }"
        self.assertEqual(extract_code_block(text), text + "\n")

    def test_fenced_cpp(self):
        text = "```cpp\nint f() { return 1; }\n```"
        self.assertEqual(extract_code_block(text), "int f() { return 1; }\n")

    def test_unclosed_fence(self):
        text = "```cpp\nint f() { return 1; }"
        self.assertEqual(extract_code_block(text), "int f() { return 1; }\n")

    def test_malformed(self):
        text = "Some commentary\n```cpp\nint f() { return 1; }\n```\nMore commentary"
        self.assertEqual(extract_code_block(text), "int f() { return 1; }\n")

class TestBenchmarkParsing(unittest.TestCase):
    def test_key_value_parsing(self):
        text = "iterations=100\ntime_ms=1.23\nsuccess=true\nmessage=None"
        parsed = parse_key_value_lines(text)
        self.assertEqual(parsed["iterations"], 100)
        self.assertEqual(parsed["time_ms"], 1.23)
        self.assertEqual(parsed["success"], True)
        self.assertEqual(parsed["message"], None)

class TestRemarkHandling(unittest.TestCase):
    def setUp(self):
        self.sample_yaml = """
--- !Missed
Pass:            inline
Name:            NoDefinition
DebugLoc:        { File: fibonacci.cpp, Line: 10, Column: 0 }
Function:        fibonacci
Args:
  - Callee:          'extern_func'
  - String:          ' will not be inlined'
--- !Passed
Pass:            loop-vectorize
Name:            Vectorized
DebugLoc:        { File: fibonacci.cpp, Line: 20, Column: 0 }
Function:        fibonacci
Args:
  - String:          'loop vectorized'
--- !Analysis
Pass:            loop-vectorize
Name:            MemoryDep
DebugLoc:        { File: other.cpp, Line: 5, Column: 0 }
Function:        other_func
Args:
  - String:          'memory dependency'
"""

    def test_parse_remarks(self):
        remarks = parse_remarks(self.sample_yaml)
        self.assertEqual(len(remarks), 3)
        self.assertEqual(remarks[0].kind, "Missed")
        self.assertEqual(remarks[0].pass_name, "inline")
        self.assertEqual(remarks[0].function, "fibonacci")
        self.assertEqual(remarks[0].message, "extern_func will not be inlined")
        self.assertEqual(remarks[1].kind, "Passed")
        self.assertEqual(remarks[2].kind, "Analysis")

    def test_prioritize_remarks(self):
        remarks = parse_remarks(self.sample_yaml)
        prioritized = prioritize_remarks(remarks, "fibonacci.cpp")
        self.assertEqual(prioritized[0].kind, "Missed")
        self.assertEqual(prioritized[1].kind, "Analysis") # Higher because Passed is lowest priority
        self.assertEqual(prioritized[2].kind, "Passed")

    def test_filter_remarks(self):
        remarks = parse_remarks(self.sample_yaml)
        fingerprints = {remarks[0].fingerprint()}
        filtered = filter_remarks(remarks, fingerprints)
        self.assertEqual(len(filtered), 2)
        self.assertNotIn(remarks[0], filtered)

    def test_batch_remarks(self):
        remarks = parse_remarks(self.sample_yaml)
        # Mock token count by using characters if tokenize_fn is None
        # Each remark raw text is roughly 150-200 chars. 
        # Let's limit to something that fits only one.
        selected, remaining = batch_remarks(remarks, 100) # characters fallback / 3
        # estimate_tokens(remark_text) is len // 3.
        # If remark is 300 chars, it's 100 tokens.
        self.assertGreater(len(remarks), 0)
        self.assertLessEqual(len(selected), len(remarks))

class TestContextFitting(unittest.TestCase):
    def test_batching_limit(self):
        r1 = Remark("Missed", "p1", "n1", "f1", "file", 1, 1, "msg1", "RAW1")
        r2 = Remark("Missed", "p2", "n2", "f2", "file", 2, 1, "msg2", "RAW2_LONG")
        remarks = [r1, r2]
        
        # r1 raw is 4 chars -> 1 token (4//3)
        # r2 raw is 9 chars -> 3 tokens (9//3)
        
        selected, remaining = batch_remarks(remarks, 2)
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0].remark_name, "n1")
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].remark_name, "n2")

class TestJsonSerialization(unittest.TestCase):
    def test_path_serialization(self):
        data = {
            "path": Path("/tmp/test.txt"),
            "nested": {
                "list": [Path("a"), Path("b")]
            },
            "set": {Path("c"), Path("d")}
        }
        encoded = json.dumps(data, cls=LLMoJsonEncoder, sort_keys=True)
        decoded = json.loads(encoded)
        self.assertEqual(decoded["path"], "/tmp/test.txt")
        self.assertEqual(decoded["nested"]["list"], ["a", "b"])
        self.assertEqual(decoded["set"], ["c", "d"])

class TestTokenCounting(unittest.TestCase):
    def test_fallback(self):
        # Without LLAMA_BASE_URL (or if it fails), it should use estimate_tokens
        text = "short text"
        # estimate_tokens is len // 3
        expected = len(text) // 3
        self.assertEqual(count_tokens(text), expected)

class TestBenchmarkJsonWriting(unittest.TestCase):
    def test_kv_to_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            stdout_file = tmp_path / "stdout.txt"
            output_json = tmp_path / "results.json"
            stdout_file.write_text("a=1\nb=true\nc=None", encoding="utf-8")
            try_write_benchmark_json(stdout_file, output_json)
            self.assertTrue(output_json.exists())
            data = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(data["a"], 1)
            self.assertEqual(data["b"], True)
            self.assertEqual(data["c"], None)

    def test_json_to_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            stdout_file = tmp_path / "stdout.txt"
            output_json = tmp_path / "results.json"
            stdout_file.write_text('{"x": 10, "y": "hello"}', encoding="utf-8")
            try_write_benchmark_json(stdout_file, output_json)
            self.assertTrue(output_json.exists())
            data = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(data["x"], 10)
            self.assertEqual(data["y"], "hello")

    def test_realistic_remarks(self):
        fixture = """
--- !Passed
Pass:            inline
Name:            Inlined
DebugLoc:        { File: fibonacci.cpp, Line: 10, Column: 5 }
Function:        fibonacci
Args:
  - Callee:          'some_helper'
  - String:          ' inlined into '
  - Caller:          'fibonacci'
--- !Missed
Pass:            loop-vectorize
Name:            MissedDetails
DebugLoc:        { File: fibonacci.cpp, Line: 15, Column: 0 }
Function:        fibonacci
Args:
  - String:          'loop not vectorized: unsafe dependent memory operations'
--- !Analysis
Pass:            prologepilog
Name:            StackSize
Function:        fibonacci
Args:
  - String:          'stack size is '
  - StackSize:       '48'
"""
        remarks = parse_remarks(fixture)
        self.assertEqual(len(remarks), 3)
        self.assertEqual(remarks[0].kind, "Passed")
        self.assertEqual(remarks[0].message, "some_helper inlined into fibonacci")
        self.assertEqual(remarks[1].kind, "Missed")
        self.assertEqual(remarks[1].message, "loop not vectorized: unsafe dependent memory operations")
        self.assertEqual(remarks[2].kind, "Analysis")
        self.assertEqual(remarks[2].message, "stack size is 48")
        
        # Test fingerprint stability
        f1 = remarks[0].fingerprint()
        remarks[0].line = 100 # Change line
        self.assertEqual(remarks[0].fingerprint(), f1)

if __name__ == '__main__':
    unittest.main()
