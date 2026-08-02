import unittest
from pathlib import Path
from llmo.naming import sanitize_identifier, make_artifact_id, get_standard_path

class TestNaming(unittest.TestCase):
    def test_sanitize_identifier(self):
        self.assertEqual(sanitize_identifier("Qwen2.5-Coder-14B-Instruct-GGUF:Q4_K_M"), "qwen2-5-coder-14b-instruct-gguf-q4_k_m")
        self.assertEqual(sanitize_identifier("fibonacci.cpp"), "fibonacci_cpp")
        self.assertEqual(sanitize_identifier("Some__ID"), "some_id")
        self.assertEqual(sanitize_identifier("Multiple---Dashes"), "multiple-dashes")

    def test_make_artifact_id(self):
        aid = make_artifact_id("naive-cpp", "count_matches", model_id="qwen2.5-coder")
        self.assertEqual(aid, "naive-cpp__qwen2-5-coder__count_matches")
        
        aid = make_artifact_id("llvm", "fibonacci", pipeline_id="cpp-clang-o3")
        self.assertEqual(aid, "llvm__fibonacci__cpp-clang-o3")

    def test_get_standard_path(self):
        root = Path("/tmp/results")
        path = get_standard_path(root, "naive-cpp", "run123", "art456")
        expected = root / "naive-cpp" / "run123" / "artifacts" / "art456"
        self.assertEqual(path, expected)

if __name__ == "__main__":
    unittest.main()
