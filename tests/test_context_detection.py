import unittest
from pathlib import Path
import json
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

# Mock config before importing llama to avoid issues with missing env vars if any
with patch('llmo.config.LLAMA_CTX_SIZE', 32768), \
     patch('llmo.config.LLAMA_BASE_URL', 'http://127.0.0.1:8001'):
    from llmo import llama

class TestContextDetection(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.log_dir = self.test_dir / "logs"
        self.log_dir.mkdir()
        self.stderr_path = self.log_dir / "llama_server_stderr.txt"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    @patch('llmo.llama.http_json')
    def test_four_8192_slots(self, mock_http_json):
        # Scenario: four 8192-token slots resulting in an effective context of 8192
        mock_http_json.side_effect = lambda method, url, **kwargs: (
            [{"id": 0, "n_ctx": 8192}, {"id": 1, "n_ctx": 8192}, {"id": 2, "n_ctx": 8192}, {"id": 3, "n_ctx": 8192}]
            if "/slots" in url else {}
        )
        
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 8192)
        self.assertEqual(llama.EFFECTIVE_LLAMA_CTX_SIZE, 8192)

    @patch('llmo.llama.http_json')
    def test_one_32768_slot(self, mock_http_json):
        # Scenario: one 32768-token slot resulting in 32768
        mock_http_json.side_effect = lambda method, url, **kwargs: (
            [{"id": 0, "n_ctx": 32768}]
            if "/slots" in url else {}
        )
        
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 32768)

    @patch('llmo.llama.http_json')
    def test_one_model_capped_16384_slot(self, mock_http_json):
        # Scenario: one model-capped 16384-token slot resulting in 16384
        mock_http_json.side_effect = lambda method, url, **kwargs: (
            [{"id": 0, "n_ctx": 16384}]
            if "/slots" in url else {}
        )
        
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 16384)

    @patch('llmo.llama.http_json')
    def test_slots_unavailable_fallback_to_props(self, mock_http_json):
        # Scenario: /slots unavailable, fallback to /props.default_generation_settings.n_ctx
        def mock_side_effect(method, url, **kwargs):
            if "/slots" in url:
                raise Exception("Not found")
            if "/props" in url:
                return {"default_generation_settings": {"n_ctx": 20480}}
            return {}
            
        mock_http_json.side_effect = mock_side_effect
        
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 20480)

    @patch('llmo.llama.http_json')
    def test_slots_props_unavailable_fallback_to_logs(self, mock_http_json):
        # Scenario: API unavailable, fallback to logs slot ctx
        mock_http_json.side_effect = Exception("API down")
        self.stderr_path.write_text("slot 0, n_ctx 4096\n")
        
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 4096)

    @patch('llmo.llama.http_json')
    def test_full_fallback_chain(self, mock_http_json):
        # Scenario: only n_ctx_train in logs
        mock_http_json.side_effect = Exception("API down")
        self.stderr_path.write_text("llm_load_print_meta: n_ctx_train = 8192\n")
        
        # requested 32768, train 8192 -> 8192
        ctx = llama.detect_effective_context(self.log_dir)
        self.assertEqual(ctx, 8192)

if __name__ == '__main__':
    unittest.main()
