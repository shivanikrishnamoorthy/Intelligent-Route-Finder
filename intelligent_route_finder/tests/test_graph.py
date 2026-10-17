"""
Unit Tests for Graph Data Structure
===================================
Tests graph construction, adjacency list, edge weights, connectivity, and serialization.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.graph import Graph, Vertex, Edge


class TestGraph:
    def test_vertex_addition(self):
        g = Graph(name="Test Network")
        v = g.add_vertex("A", x=10.0, y=20.0, category="Hub", description="Test Hub")
        assert g.vertex_count == 1
        assert "A" in g.vertices
        assert v.x == 10.0
        assert v.y == 20.0

        # Updating existing vertex
        v_updated = g.add_vertex("A", x=15.0, y=25.0)
        assert g.vertex_count == 1
        assert v_updated.x == 15.0

    def test_empty_vertex_name_raises_error(self):
        g = Graph()
        with pytest.raises(ValueError):
            g.add_vertex("")

    def test_edge_addition_bidirectional(self):
        g = Graph()
        g.add_edge("A", "B", 12.5, road_name="Main St", bidirectional=True)
        assert g.vertex_count == 2
        assert g.edge_count == 1

        neighbors_a = g.get_neighbors("A")
        assert len(neighbors_a) == 1
        assert neighbors_a[0] == ("B", 12.5)

        neighbors_b = g.get_neighbors("B")
        assert len(neighbors_b) == 1
        assert neighbors_b[0] == ("A", 12.5)

    def test_negative_weight_rejected(self):
        g = Graph()
        with pytest.raises(ValueError, match="non-negative"):
            g.add_edge("A", "B", -5.0)

    def test_zero_weight_allowed(self):
        g = Graph()
        g.add_edge("A", "B", 0.0)
        assert g.edge_count == 1
        assert g.get_neighbors("A")[0][1] == 0.0

    def test_edge_removal(self):
        g = Graph()
        g.add_edge("A", "B", 10.0)
        g.add_edge("B", "C", 20.0)
        assert g.edge_count == 2

        removed = g.remove_edge("A", "B")
        assert removed is True
        assert g.edge_count == 1
        assert len(g.get_neighbors("A")) == 0

    def test_vertex_removal_cleans_incident_edges(self):
        g = Graph()
        g.add_edge("A", "B", 5.0)
        g.add_edge("B", "C", 10.0)
        g.add_edge("A", "C", 15.0)

        assert g.vertex_count == 3
        g.remove_vertex("B")
        assert g.vertex_count == 2
        assert "B" not in g.vertices

        # Edges touching B should be gone
        assert g.get_neighbors("A") == [("C", 15.0)]
        assert g.get_neighbors("C") == [("A", 15.0)]

    def test_connectivity(self):
        g = Graph()
        g.add_edge("A", "B", 1.0)
        g.add_edge("B", "C", 2.0)
        assert g.is_connected() is True

        # Add isolated vertex
        g.add_vertex("Isolated")
        assert g.is_connected() is False

    def test_csv_serialization_roundtrip(self):
        g = Graph(name="Original")
        g.add_edge("A", "B", 4.5, road_name="RoadAB")
        g.add_edge("B", "C", 7.2, road_name="RoadBC")

        csv_text = g.to_csv_edge_list()
        imported = Graph.from_csv_edge_list(csv_text, name="Imported")

        assert imported.vertex_count == 3
        assert imported.edge_count == 2
        assert len(imported.get_neighbors("A")) == 1
        assert imported.get_neighbors("A")[0] == ("B", 4.5)
