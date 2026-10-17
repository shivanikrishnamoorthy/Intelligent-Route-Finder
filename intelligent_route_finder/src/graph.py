"""
Graph Data Structure Implementation
===================================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Features:
- Adjacency list representation: Map of Vertex -> List of (neighbor, weight).
- Support for 2D spatial coordinates (x, y) for visual rendering and realistic road networks.
- Strict non-negative weight validation for Dijkstra preconditions.
- Bidirectional (undirected) and directed edge support.
- Graph serialization (Dictionary, JSON, CSV edge-list).
- Graph connectivity and topology inspection helpers.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import json
import math
import random


class Vertex:
    """Represents a location/node in the road network."""

    def __init__(
        self,
        name: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        category: str = "Location",
        description: str = "",
    ):
        self.name = str(name).strip()
        self.x = float(x) if x is not None else 0.0
        self.y = float(y) if y is not None else 0.0
        self.category = category
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vertex":
        return cls(
            name=data["name"],
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            category=data.get("category", "Location"),
            description=data.get("description", ""),
        )

    def __repr__(self) -> str:
        return f"Vertex({self.name}, pos=({self.x:.2f}, {self.y:.2f}))"


class Edge:
    """Represents a road/weighted connection between two vertices."""

    def __init__(
        self,
        source: str,
        target: str,
        weight: float,
        road_name: str = "",
        bidirectional: bool = True,
    ):
        if weight < 0:
            raise ValueError(f"Edge weight cannot be negative ({weight}). Dijkstra requires w(u,v) >= 0.")
        self.source = str(source).strip()
        self.target = str(target).strip()
        self.weight = float(weight)
        self.road_name = road_name or f"{self.source}-{self.target}"
        self.bidirectional = bidirectional

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "road_name": self.road_name,
            "bidirectional": self.bidirectional,
        }

    def __repr__(self) -> str:
        arrow = "<->" if self.bidirectional else "->"
        return f"Edge({self.source} {arrow} {self.target}, w={self.weight:.2f})"


class Graph:
    """
    Adjacency List Graph for Road Networks.
    Nodes are identified by unique string keys.
    """

    def __init__(self, name: str = "Road Network", directed: bool = False):
        self.name = name
        self.directed = directed
        # vertices: dict of name -> Vertex
        self.vertices: Dict[str, Vertex] = {}
        # adj: dict of name -> list of (neighbor_name, weight, edge_obj)
        self.adj: Dict[str, List[Tuple[str, float, Edge]]] = {}

    def add_vertex(
        self,
        name: str,
        x: Optional[float] = None,
        y: Optional[float] = None,
        category: str = "Location",
        description: str = "",
    ) -> Vertex:
        """Add a vertex to the graph. If vertex already exists, updates coordinates/metadata."""
        v_name = str(name).strip()
        if not v_name:
            raise ValueError("Vertex name cannot be empty.")

        if v_name in self.vertices:
            v = self.vertices[v_name]
            if x is not None:
                v.x = float(x)
            if y is not None:
                v.y = float(y)
            if category:
                v.category = category
            if description:
                v.description = description
            return v

        vertex = Vertex(v_name, x, y, category, description)
        self.vertices[v_name] = vertex
        self.adj[v_name] = []
        return vertex

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float,
        road_name: str = "",
        bidirectional: Optional[bool] = None,
    ) -> Edge:
        """
        Add a weighted edge between source and target.
        If vertices do not exist, they will be auto-created.
        Edge weights must be non-negative.
        """
        s_name = str(source).strip()
        t_name = str(target).strip()
        if not s_name or not t_name:
            raise ValueError("Edge endpoints cannot be empty.")
        if weight < 0:
            raise ValueError(f"Dijkstra algorithm requires non-negative edge weights; received {weight}.")

        if s_name not in self.vertices:
            self.add_vertex(s_name)
        if t_name not in self.vertices:
            self.add_vertex(t_name)

        if bidirectional is None:
            bidirectional = not self.directed

        # Check if edge already exists, update weight if so
        self._remove_direct_edge(s_name, t_name)
        edge = Edge(s_name, t_name, weight, road_name, bidirectional=bidirectional)
        self.adj[s_name].append((t_name, float(weight), edge))

        if bidirectional and s_name != t_name:
            self._remove_direct_edge(t_name, s_name)
            rev_edge = Edge(t_name, s_name, weight, road_name, bidirectional=True)
            self.adj[t_name].append((s_name, float(weight), rev_edge))

        return edge

    def _remove_direct_edge(self, u: str, v: str) -> None:
        """Helper to remove directed edge u -> v if present."""
        if u in self.adj:
            self.adj[u] = [item for item in self.adj[u] if item[0] != v]

    def remove_edge(self, u: str, v: str, bidirectional: bool = True) -> bool:
        """Remove an edge between u and v."""
        u_name, v_name = str(u).strip(), str(v).strip()
        removed = False
        if u_name in self.adj:
            before_len = len(self.adj[u_name])
            self.adj[u_name] = [item for item in self.adj[u_name] if item[0] != v_name]
            if len(self.adj[u_name]) < before_len:
                removed = True

        if bidirectional and v_name in self.adj:
            before_len = len(self.adj[v_name])
            self.adj[v_name] = [item for item in self.adj[v_name] if item[0] != u_name]
            if len(self.adj[v_name]) < before_len:
                removed = True
        return removed

    def remove_vertex(self, name: str) -> bool:
        """Remove vertex and all its connected incident edges."""
        v_name = str(name).strip()
        if v_name not in self.vertices:
            return False

        del self.vertices[v_name]
        del self.adj[v_name]

        # Remove all incident edges in other adjacency lists
        for u in self.adj:
            self.adj[u] = [item for item in self.adj[u] if item[0] != v_name]
        return True

    def get_neighbors(self, u: str) -> List[Tuple[str, float]]:
        """Return list of (neighbor_name, weight) outgoing from u."""
        u_name = str(u).strip()
        if u_name not in self.adj:
            return []
        return [(neighbor, weight) for neighbor, weight, _ in self.adj[u_name]]

    def get_vertex(self, name: str) -> Optional[Vertex]:
        return self.vertices.get(str(name).strip())

    def get_all_vertices(self) -> List[str]:
        return list(self.vertices.keys())

    def get_all_edges(self) -> List[Tuple[str, str, float, str]]:
        """Return list of unique edges: (source, target, weight, road_name)."""
        edges_seen: Set[Tuple[str, str]] = set()
        result = []

        for u, nbrs in self.adj.items():
            for v, weight, edge_obj in nbrs:
                edge_key = (min(u, v), max(u, v)) if edge_obj.bidirectional else (u, v)
                if edge_key not in edges_seen:
                    edges_seen.add(edge_key)
                    result.append((u, v, weight, edge_obj.road_name))
        return result

    @property
    def vertex_count(self) -> int:
        return len(self.vertices)

    @property
    def edge_count(self) -> int:
        return len(self.get_all_edges())

    def degree(self, u: str) -> int:
        """Return out-degree (or incident degree for undirected graph) of vertex u."""
        u_name = str(u).strip()
        return len(self.adj.get(u_name, []))

    def compute_density(self) -> float:
        """
        Compute density of graph:
        D = 2|E| / (|V|(|V|-1)) for undirected, |E| / (|V|(|V|-1)) for directed.
        """
        v = self.vertex_count
        if v <= 1:
            return 0.0
        e = self.edge_count
        max_edges = v * (v - 1) if self.directed else (v * (v - 1)) / 2.0
        return round(e / max_edges, 4)

    def is_connected(self) -> bool:
        """Check if graph is connected (or weakly connected for directed)."""
        if self.vertex_count <= 1:
            return True

        # Run BFS from the first vertex
        start = next(iter(self.vertices.keys()))
        visited: Set[str] = set()
        queue = [start]
        visited.add(start)

        while queue:
            curr = queue.pop(0)
            for nbr, _, edge_obj in self.adj.get(curr, []):
                if nbr not in visited:
                    visited.add(nbr)
                    queue.append(nbr)

        # In an undirected graph, connected if all vertices were reached
        return len(visited) == self.vertex_count

    def auto_layout_if_missing(self) -> None:
        """Assign circular or force-directed coordinates if coordinates are missing (0,0)."""
        all_zeros = all(v.x == 0.0 and v.y == 0.0 for v in self.vertices.values())
        if all_zeros and len(self.vertices) > 0:
            n = len(self.vertices)
            radius = 100.0
            for idx, (name, v) in enumerate(self.vertices.items()):
                angle = 2 * math.pi * idx / n
                v.x = round(radius * math.cos(angle), 2)
                v.y = round(radius * math.sin(angle), 2)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary."""
        return {
            "name": self.name,
            "directed": self.directed,
            "vertices": [v.to_dict() for v in self.vertices.values()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "weight": w,
                    "road_name": road,
                }
                for u, v, w, road in self.get_all_edges()
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        """Deserialize graph from dictionary."""
        g = cls(name=data.get("name", "Road Network"), directed=data.get("directed", False))
        for v_data in data.get("vertices", []):
            g.add_vertex(
                name=v_data["name"],
                x=v_data.get("x", 0.0),
                y=v_data.get("y", 0.0),
                category=v_data.get("category", "Location"),
                description=v_data.get("description", ""),
            )
        for e_data in data.get("edges", []):
            g.add_edge(
                source=e_data["source"],
                target=e_data["target"],
                weight=float(e_data["weight"]),
                road_name=e_data.get("road_name", ""),
                bidirectional=not g.directed,
            )
        return g

    def to_csv_edge_list(self) -> str:
        """Export edge list as CSV string: source,target,weight,road_name."""
        lines = ["source,target,weight,road_name"]
        for u, v, w, road in self.get_all_edges():
            lines.append(f'"{u}","{v}",{w},"{road}"')
        return "\n".join(lines)

    @classmethod
    def from_csv_edge_list(cls, csv_text: str, name: str = "Imported Graph", directed: bool = False) -> "Graph":
        """Build graph from CSV edge list content."""
        g = cls(name=name, directed=directed)
        lines = [line.strip() for line in csv_text.strip().splitlines() if line.strip()]
        if not lines:
            return g

        # Skip header if present
        header = lines[0].lower()
        start_idx = 1 if ("source" in header and "target" in header) else 0

        for line in lines[start_idx:]:
            # Simple CSV split with quote stripping
            parts = [p.strip().strip('"').strip("'") for p in line.split(",")]
            if len(parts) >= 3:
                u, v, w_str = parts[0], parts[1], parts[2]
                road = parts[3] if len(parts) > 3 else f"{u}-{v}"
                try:
                    w = float(w_str)
                    g.add_edge(u, v, w, road_name=road)
                except ValueError:
                    continue
        g.auto_layout_if_missing()
        return g
