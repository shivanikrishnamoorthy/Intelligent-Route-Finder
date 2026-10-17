"""
Unit Tests for Custom Min-Heap Implementation
==============================================
Tests all heap operations, edge cases, invariants, and metrics.
"""

import pytest
import random
import sys
import os

# Ensure src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.min_heap import MinHeap


class TestMinHeap:
    def test_empty_heap(self):
        heap = MinHeap()
        assert len(heap) == 0
        assert heap.is_empty() is True
        assert heap.peek() is None
        assert heap.contains("A") is False
        with pytest.raises(IndexError):
            heap.extract_min()

    def test_single_element(self):
        heap = MinHeap()
        heap.insert(5.0, "Node1")
        assert len(heap) == 1
        assert heap.is_empty() is False
        assert heap.peek() == (5.0, "Node1")
        assert heap.contains("Node1") is True

        extracted = heap.extract_min()
        assert extracted == (5.0, "Node1")
        assert len(heap) == 0
        assert heap.is_empty() is True

    def test_sorted_extraction(self):
        heap = MinHeap()
        elements = [(10, "A"), (4, "B"), (15, "C"), (1, "D"), (7, "E"), (9, "F")]
        for p, item in elements:
            heap.insert(p, item)

        assert len(heap) == len(elements)
        extracted = []
        while not heap.is_empty():
            extracted.append(heap.extract_min())

        expected = sorted(elements, key=lambda x: x[0])
        assert extracted == expected

    def test_random_large_dataset(self):
        heap = MinHeap()
        random.seed(42)
        values = [(random.uniform(0.1, 1000.0), f"Item_{i}") for i in range(100)]
        for p, item in values:
            heap.insert(p, item)

        assert len(heap) == 100
        extracted_priorities = []
        while not heap.is_empty():
            p, _ = heap.extract_min()
            extracted_priorities.append(p)

        # Invariant: extracted priorities must be strictly monotonically non-decreasing
        for i in range(len(extracted_priorities) - 1):
            assert extracted_priorities[i] <= extracted_priorities[i + 1]

    def test_decrease_key(self):
        heap = MinHeap()
        heap.insert(50.0, "A")
        heap.insert(30.0, "B")
        heap.insert(80.0, "C")

        assert heap.peek() == (30.0, "B")
        # Decrease C from 80.0 to 10.0 -> should bubble up to root!
        heap.decrease_key("C", 10.0)
        assert heap.peek() == (10.0, "C")
        assert heap.get_priority("C") == 10.0

        # Decrease A from 50.0 to 5.0 -> should become new root!
        heap.decrease_key("A", 5.0)
        assert heap.peek() == (5.0, "A")

        # Invalid decrease_key (increase priority) should raise ValueError
        with pytest.raises(ValueError):
            heap.decrease_key("A", 20.0)

        # Non-existent item should raise KeyError
        with pytest.raises(KeyError):
            heap.decrease_key("NonExistent", 2.0)

    def test_insert_existing_item_with_lower_priority(self):
        heap = MinHeap()
        heap.insert(40.0, "NodeX")
        # Inserting existing item with lower priority acts as decrease_key
        heap.insert(15.0, "NodeX")
        assert len(heap) == 1
        assert heap.peek() == (15.0, "NodeX")

        # Inserting existing item with higher priority leaves it unchanged
        heap.insert(60.0, "NodeX")
        assert len(heap) == 1
        assert heap.peek() == (15.0, "NodeX")

    def test_metrics_tracking(self):
        heap = MinHeap()
        heap.insert(20.0, "A")
        heap.insert(10.0, "B")
        heap.insert(30.0, "C")
        heap.decrease_key("C", 5.0)
        heap.extract_min()

        metrics = heap.get_metrics()
        assert metrics["insertions"] == 3
        assert metrics["decrease_keys"] == 1
        assert metrics["extract_mins"] == 1
        assert metrics["comparisons"] > 0
        assert metrics["total_operations"] > 0
