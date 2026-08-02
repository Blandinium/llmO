import unittest
from llmo.benchmark_protocol import (
    BenchmarkMeasurement, 
    BenchmarkStatistics, 
    calculate_benchmark_statistics, 
    compare_benchmarks,
    BenchmarkProtocol
)

class TestBenchmarkProtocol(unittest.TestCase):
    def test_calculate_statistics_success(self):
        measurements = [
            BenchmarkMeasurement("a1", 0, "fib", 0, 0, 100.0, 1000, 900, 42, 0, {}, "out", "err"),
            BenchmarkMeasurement("a1", 0, "fib", 1, 2, 110.0, 900, 800, 42, 0, {}, "out", "err"),
            BenchmarkMeasurement("a1", 0, "fib", 2, 4, 120.0, 800, 700, 42, 0, {}, "out", "err"),
        ]
        stats = calculate_benchmark_statistics(measurements, 3)
        self.assertEqual(stats.successful_repetitions, 3)
        self.assertEqual(stats.median_calls_per_second, 110.0)
        self.assertEqual(stats.minimum_calls_per_second, 100.0)
        self.assertEqual(stats.maximum_calls_per_second, 120.0)
        self.assertAlmostEqual(stats.mean_calls_per_second, 110.0)
        self.assertEqual(stats.median_absolute_deviation, 10.0)

    def test_calculate_statistics_incomplete(self):
        measurements = [
            BenchmarkMeasurement("a1", 0, "fib", 0, 0, 100.0, 1000, 900, 42, 0, {}, "out", "err"),
            BenchmarkMeasurement("a1", 0, "fib", 1, 2, None, None, None, None, 1, None, "out", "err"),
        ]
        stats = calculate_benchmark_statistics(measurements, 2)
        self.assertEqual(stats.successful_repetitions, 1)
        self.assertEqual(stats.requested_repetitions, 2)

    def test_compare_benchmarks_improved(self):
        base_stats = BenchmarkStatistics(3, 3, 100.0, 90.0, 110.0, 100.0, 5.0)
        cand_stats = BenchmarkStatistics(3, 3, 110.0, 100.0, 120.0, 110.0, 5.0)
        
        # 10% improvement > 2.0% threshold
        comp = compare_benchmarks(cand_stats, base_stats, 2.0, "base", "cand", ["base", "cand"])
        self.assertEqual(comp.classification, "improved")
        self.assertAlmostEqual(comp.relative_change_percent, 10.0)

    def test_compare_benchmarks_regressed(self):
        base_stats = BenchmarkStatistics(3, 3, 100.0, 90.0, 110.0, 100.0, 5.0)
        cand_stats = BenchmarkStatistics(3, 3, 90.0, 80.0, 100.0, 90.0, 5.0)
        
        # 10% regression < -2.0% threshold
        comp = compare_benchmarks(cand_stats, base_stats, 2.0, "base", "cand", ["base", "cand"])
        self.assertEqual(comp.classification, "regressed")
        self.assertAlmostEqual(comp.relative_change_percent, -10.0)

    def test_compare_benchmarks_unchanged(self):
        base_stats = BenchmarkStatistics(3, 3, 100.0, 90.0, 110.0, 100.0, 5.0)
        cand_stats = BenchmarkStatistics(3, 3, 101.0, 95.0, 105.0, 101.0, 2.0)
        
        # 1% improvement <= 2.0% threshold
        comp = compare_benchmarks(cand_stats, base_stats, 2.0, "base", "cand", ["base", "cand"])
        self.assertEqual(comp.classification, "unchanged_within_noise")

    def test_compare_benchmarks_failed(self):
        base_stats = BenchmarkStatistics(3, 0)
        cand_stats = BenchmarkStatistics(3, 3, 100.0)
        comp = compare_benchmarks(cand_stats, base_stats, 2.0, "base", "cand", [])
        self.assertEqual(comp.classification, "benchmark_failed")

    def test_compare_benchmarks_incomplete(self):
        base_stats = BenchmarkStatistics(3, 2, 100.0)
        cand_stats = BenchmarkStatistics(3, 3, 110.0)
        comp = compare_benchmarks(cand_stats, base_stats, 2.0, "base", "cand", [])
        self.assertEqual(comp.classification, "benchmark_incomplete")

if __name__ == "__main__":
    unittest.main()
