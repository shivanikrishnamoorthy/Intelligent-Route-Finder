"""
Unit Tests for Dijkstra Shortest-Path Implementations
=====================================================
Covers standard search, algorithm parity (Min-Heap vs Unsorted List),
disconnected graphs, source==destination, alternative routes, and edge cases.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.graph import Graph
from src.dijkstra import dijkstra_min_heap, dijkstra_unsorted_list
from src.sample_data import create_smart_metro_network, create_disconnected_network


class TestDijkstra:
    def setup_method(self):
        """Build standard textbook test graph."""
        # A - (4) - B - (1) - C
        # |         |         |
        # (2)      (1)       (5)
        # |         |         |
        # D - (8) - E - (2) - F
        self.g = Graph(name="Textbook Test Graph", directed=False)
        self.g.add_edge("A", "B", 4.0)
        self.g.add_edge("A", "D", 2.0)
        self.g.add_edge("B", "C", 1.0)
        self.g.add_edge("B", "E", 1.0)
        self.g.add_edge("C", "F", 5.0)
        self.g.add_edge("D", "E", 8.0)
        self.g.add_edge("E", "F", 2.0)

    def test_standard_shortest_path(self):
        # Path from A to F:
        # A -> B -> E -> F (cost: 4 + 1 + 2 = 7)
        # or A -> D -> E -> F (cost: 2 + 8 + 2 = 12)
        # or A -> B -> C -> F (cost: 4 + 1 + 5 = 10)
        res_heap, _ = dijkstra_min_heap(self.g, source="A", target="F")
        assert res_heap.is_reachable("F") is True
        assert res_heap.get_distance("F") == 7.0
        assert res_heap.get_path("F") == ["A", "B", "E", "F"]

    def test_min_heap_and_unsorted_list_parity(self):
        """Min-Heap and Unsorted-List implementations must produce identical results."""
        metro = create_smart_metro_network()
        source = "Central Station"

        res_heap, _ = dijkstra_min_heap(metro, source=source)
        res_list = dijkstra_unsorted_list(metro, source=source)

        for v in metro.get_all_vertices():
            heap_dist = res_heap.get_distance(v)
            list_dist = res_list.get_distance(v)
            assert pytest.approx(heap_dist, 0.001) == list_dist
            if heap_dist < float("inf"):
                # Path lengths should match exactly
                assert len(res_heap.get_path(v)) == len(res_list.get_path(v))

    def test_source_equals_destination(self):
        """Edge case: source == destination."""
        res, _ = dijkstra_min_heap(self.g, source="A", target="A")
        assert res.get_distance("A") == 0.0
        assert res.get_path("A") == ["A"]
        assert res.get_path_edges("A") == []

        res_list = dijkstra_unsorted_list(self.g, source="A", target="A")
        assert res_list.get_distance("A") == 0.0
        assert res_list.get_path("A") == ["A"]

    def test_disconnected_graph_unreachable(self):
        """Edge case: disconnected graphs and unreachable vertices."""
        disc_graph = create_disconnected_network()
        # Mainland Port -> Island Lighthouse should be completely unreachable
        res, _ = dijkstra_min_heap(disc_graph, source="Mainland Port")

        assert res.is_reachable("Capital City") is True
        assert res.is_reachable("Island Lighthouse") is False
        assert res.get_distance("Island Lighthouse") == float("inf")
        assert res.get_path("Island Lighthouse") == []
        assert "Island Lighthouse" in res.get_unreachable_vertices()
        assert len(res.get_unreachable_vertices()) == 3

    def test_alternative_routes_optimization(self):
        """Verifies algorithm selects strictly shortest route among multiple paths."""
        g = Graph()
        # Direct route A -> B is 100
        g.add_edge("A", "B", 100.0)
        # Detour route A -> C -> D -> B is 10 + 20 + 30 = 60
        g.add_edge("A", "C", 10.0)
        g.add_edge("C", "D", 20.0)
        g.add_edge("D", "B", 30.0)

        res, _ = dijkstra_min_heap(g, source="A", target="B")
        assert res.get_distance("B") == 60.0
        assert res.get_path("B") == ["A", "C", "D", "B"]

    def test_zero_weight_edges(self):
        """Edge case: zero-weight edges."""
        g = Graph()
        g.add_edge("A", "B", 0.0)
        g.add_edge("B", "C", 5.0)

        res, _ = dijkstra_min_heap(g, source="A")
        assert res.get_distance("B") == 0.0
        assert res.get_distance("C") == 5.0
        assert res.get_path("C") == ["A", "B", "C"]

    def test_invalid_source_or_target(self):
        """Edge case: non-existent vertices raise ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            dijkstra_min_heap(self.g, source="NonExistentNode")

        with pytest.raises(ValueError, match="does not exist"):
            dijkstra_min_heap(self.g, source="A", target="NonExistentTarget")

    def test_step_tracking(self):
        """Verifies step logging for the interactive animation visualizer."""
        res, steps = dijkstra_min_heap(self.g, source="A", track_steps=True)
        assert len(steps) > 0
        actions = [s.action for s in steps]
        assert "INIT" in actions
        assert "EXTRACT_MIN" in actions
        assert "RELAX" in actions
        assert "COMPLETE" in actions
