import unittest
from unittest.mock import patch, MagicMock, mock_open
import platform
import subprocess
from llmo.metadata import get_cpu_info, get_llama_server_version, get_run_metadata

class TestMetadata(unittest.TestCase):
    @patch("platform.processor", return_value="Intel")
    @patch("platform.machine", return_value="x86_64")
    @patch("os.cpu_count", return_value=8)
    @patch("sys.platform", "linux")
    @patch("builtins.open", new_callable=mock_open, read_data="model name : AMD Ryzen 7\n")
    @patch("subprocess.check_output")
    def test_get_cpu_info_linux(self, mock_lscpu, mock_file, mock_cpu_count, mock_machine, mock_processor):
        mock_lscpu.return_value = "0,0\n0,0\n1,0\n1,0\n"
        info = get_cpu_info()
        self.assertEqual(info["host_cpu"], "AMD Ryzen 7")
        self.assertEqual(info["cpu_architecture"], "x86_64")
        self.assertEqual(info["logical_cpu_count"], 8)
        self.assertEqual(info["physical_core_count"], 2)

    @patch("platform.processor", return_value="")
    @patch("sys.platform", "darwin")
    def test_get_cpu_info_fallback(self, mock_processor):
        info = get_cpu_info()
        self.assertEqual(info["host_cpu"], "unknown")

    @patch("subprocess.run")
    def test_get_llama_server_version_success(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "llama-server version 1.2.3\n"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc
        
        details = get_llama_server_version("llama-server")
        self.assertEqual(details["version"], "llama-server version 1.2.3")
        self.assertEqual(details["returncode"], 0)

    @patch("subprocess.run")
    def test_get_llama_server_version_failure(self, mock_run):
        mock_run.side_effect = Exception("Binary missing")
        details = get_llama_server_version("missing-server")
        self.assertEqual(details["version"], "unknown")
        self.assertIn("Binary missing", details["stderr"])

    @patch("llmo.metadata.get_cpu_info")
    @patch("llmo.metadata.get_llama_server_version")
    @patch("llmo.metadata.get_tool_version", return_value="1.0")
    @patch("socket.gethostname", return_value="test-host")
    @patch("platform.release", return_value="5.4.0")
    def test_get_run_metadata(self, mock_release, mock_hostname, mock_tool, mock_llama, mock_cpu):
        mock_cpu.return_value = {"host_cpu": "Test CPU"}
        mock_llama.return_value = {"version": "2.0", "details": "some details"}
        
        meta = get_run_metadata()
        self.assertEqual(meta["host_cpu"], "Test CPU")
        self.assertEqual(meta["llama_server_version"], "2.0")
        self.assertEqual(meta["hostname"], "test-host")

if __name__ == "__main__":
    unittest.main()
