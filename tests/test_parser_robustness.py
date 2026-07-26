import unittest
from llmo.remarks import parse_remarks

class TestParserRobustness(unittest.TestCase):
    def test_various_debugloc_shapes(self):
        # 1. Standard single line
        yaml1 = """--- !Passed
Pass:            inline
Name:            Inlined
DebugLoc:        { File: fibonacci.cpp, Line: 10, Column: 5 }
Function:        fibonacci
Args: []
"""
        # 2. Multi-line
        yaml2 = """--- !Analysis
Pass:            loop-vectorize
Name:            NonReductionValueUsedOutsideLoop
DebugLoc:        { File: 'source_output.cpp', 
                   Line: 10, Column: 5 }
Function:        fibonacci
Args: []
"""
        # 3. Scalar/Unexpected
        yaml3 = """--- !Missed
Pass:            regalloc
Name:            Spill
DebugLoc:        "some unexpected scalar"
Function:        fibonacci
Args: []
"""
        # 4. Absent
        yaml4 = """--- !Passed
Pass:            tailcallelim
Name:            Eliminated
Function:        fibonacci
Args: []
"""
        # 5. Null/Empty
        yaml5 = """--- !Analysis
Pass:            asm-printer
Name:            InstructionMix
DebugLoc:        {}
Function:        fibonacci
Args: []
"""

        content = yaml1 + yaml2 + yaml3 + yaml4 + yaml5
        remarks = parse_remarks(content)
        self.assertEqual(len(remarks), 5)
        
        self.assertEqual(remarks[0].file, "fibonacci.cpp")
        self.assertEqual(remarks[0].line, 10)
        
        self.assertEqual(remarks[1].file, "source_output.cpp")
        self.assertEqual(remarks[1].line, 10)
        
        self.assertIsNone(remarks[2].file)
        self.assertIsNone(remarks[2].line)
        
        self.assertIsNone(remarks[3].file)
        self.assertIsNone(remarks[4].file)

    def test_args_robustness(self):
        yaml = """--- !Analysis
Pass:            inline
Name:            NoDefinition
Args:
  - Callee:          'extern_func'
  - String:          ' will not be inlined'
  - DebugLoc:        { File: other.h, Line: 1 }
"""
        remarks = parse_remarks(yaml)
        self.assertEqual(len(remarks), 1)
        # Message should include the str() of the DebugLoc dict in Args
        self.assertIn("extern_func will not be inlined", remarks[0].message)
        self.assertIn("other.h", remarks[0].message)

    def test_real_failing_record(self):
        # Subset of the real failing record
        yaml = """--- !Analysis
Pass:            loop-vectorize
Name:            NonReductionValueUsedOutsideLoop
DebugLoc:        { File: 'benchmark-builds/llm-cpp-remarks/qwen2_5_coder_14b_q4km/fibonacci_cpp/iteration_01/attempt_01/source_output.cpp', 
                   Line: 10, Column: 5 }
Function:        fibonacci
Args:
  - String:          'loop not vectorized: '
  - String:          value that could not be identified as reduction is used outside the loop
...
"""
        remarks = parse_remarks(yaml)
        self.assertEqual(len(remarks), 1)
        self.assertEqual(remarks[0].kind, "Analysis")
        self.assertEqual(remarks[0].line, 10)
        self.assertTrue("source_output.cpp" in remarks[0].file)

    def test_parser_isolation(self):
        yaml = """--- !Passed
Pass: ok1
--- !Malformed
This is not a valid remark.
--- !Missed
Pass: ok2
"""
        remarks = parse_remarks(yaml)
        # It should parse !Passed, !Malformed (as a minimally populated remark), and !Missed.
        self.assertEqual(len(remarks), 3)
        self.assertEqual(remarks[0].pass_name, "ok1")
        self.assertEqual(remarks[1].kind, "Malformed")
        self.assertEqual(remarks[2].pass_name, "ok2")

if __name__ == "__main__":
    unittest.main()
