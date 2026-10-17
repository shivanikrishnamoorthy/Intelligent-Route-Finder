"""
Unit Tests for Benchmark Engine and Synthetic Graph Generator
=============================================================
Verifies graph generator guarantees and benchmark suites.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.benchmark import generate_random_connected_graph, run_benchmark_suite


class TestBenchmark:
    def test_synthetic_graph_connected(self):
        g = generate_random_connected_graph(num_vertices=20, density=0.25, seed=42)
        assert g.vertex_count == 20
        assert g.edge_count >= 19  # Tree has at least V-1 edges
        assert g.is_connected() is True

    def test_benchmark_suite_execution(self):
        # Run a micro-benchmark suite on small graphs to ensure calculations succeed
        results = run_benchmark_suite(vertex_sizes=[10, 20], density=0.3, runs_per_size=2)
        assert len(results) == 2
        for r in results:
            assert r["Vertices (V)"] in [10, 20]
            assert r["Min-Heap Time (ms)"] >= 0.0
            assert r["Unsorted-List Time (ms)"] >= 0.0
            assert r["Min-Heap Comparisons"] > 0
            assert r["Unsorted-List Comparisons"] > 0
