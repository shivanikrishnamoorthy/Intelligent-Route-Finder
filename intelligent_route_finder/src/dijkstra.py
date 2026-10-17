"""
Dijkstra's Shortest-Path Algorithm Implementations
==================================================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Implements:
1. `dijkstra_min_heap`: Shortest-path using custom MinHeap with O((V + E) log V) time.
   Supports full execution-step logging for the animated visualizer.
2. `dijkstra_unsorted_list`: Shortest-path using simple unsorted linear scan with O(V^2 + E) time.
3. `DijkstraResult`: Unified result class containing distances, predecessors, routes,
   unreachable nodes, and detailed algorithmic statistics.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import time
from .graph import Graph
from .min_heap import MinHeap


class DijkstraResult:
    """
    Encapsulates results and DSA metrics from a Dijkstra algorithm execution.
    """

    def __init__(
        self,
        algorithm_name: str,
        source: str,
        distances: Dict[str, float],
        predecessors: Dict[str, Optional[str]],
        visited_order: List[str],
        execution_time_ms: float,
        vertices_visited_count: int,
        edges_examined_count: int,
        edge_relaxations_count: int,
        heap_metrics: Optional[Dict[str, int]] = None,
        comparisons_count: int = 0,
    ):
        self.algorithm_name = algorithm_name
        self.source = source
        self.distances = distances
        self.predecessors = predecessors
        self.visited_order = visited_order
        self.execution_time_ms = execution_time_ms
        self.vertices_visited_count = vertices_visited_count
        self.edges_examined_count = edges_examined_count
        self.edge_relaxations_count = edge_relaxations_count
        self.heap_metrics = heap_metrics or {}
        self.comparisons_count = comparisons_count

    def is_reachable(self, target: str) -> bool:
        """Check if target node can be reached from source."""
        dist = self.distances.get(target, float("inf"))
        return dist < float("inf")

    def get_distance(self, target: str) -> float:
        """Return shortest distance to target."""
        return self.distances.get(target, float("inf"))

    def get_path(self, target: str) -> List[str]:
        """
        Reconstruct shortest path from source to target using predecessors.
        Returns empty list if target is unreachable.
        """
        if not self.is_reachable(target):
            return []
        if target == self.source:
            return [self.source]

        path = []
        curr: Optional[str] = target
        visited_in_reconstruction: Set[str] = set()

        while curr is not None:
            if curr in visited_in_reconstruction:
                # Safety check against unexpected cycles
                break
            visited_in_reconstruction.add(curr)
            path.append(curr)
            curr = self.predecessors.get(curr)

        path.reverse()
        if path and path[0] == self.source:
            return path
        return []

    def get_path_edges(self, target: str) -> List[Tuple[str, str]]:
        """Return list of directed pairs (u, v) along the shortest path to target."""
        path = self.get_path(target)
        if len(path) < 2:
            return []
        return [(path[i], path[i + 1]) for i in range(len(path) - 1)]

    def get_unreachable_vertices(self) -> List[str]:
        """Return list of all vertices that cannot be reached from source."""
        return [v for v, d in self.distances.items() if d == float("inf")]

    def get_reachable_vertices(self) -> List[str]:
        """Return list of vertices reachable from source."""
        return [v for v, d in self.distances.items() if d < float("inf")]

    def summary_stats(self) -> Dict[str, Any]:
        """Return summary metrics for the statistics dashboard."""
        return {
            "Algorithm": self.algorithm_name,
            "Source": self.source,
            "Total Vertices in Graph": len(self.distances),
            "Vertices Settled": self.vertices_visited_count,
            "Reachable Vertices": len(self.get_reachable_vertices()),
            "Unreachable Vertices": len(self.get_unreachable_vertices()),
            "Edges Examined": self.edges_examined_count,
            "Edge Relaxations": self.edge_relaxations_count,
            "Execution Time (ms)": round(self.execution_time_ms, 4),
            "Comparisons": self.comparisons_count,
            "Heap Total Ops": self.heap_metrics.get("total_operations", 0),
        }


class AlgorithmStep:
    """Represents a single atomic step of Dijkstra's algorithm for visualization."""

    def __init__(
        self,
        step_number: int,
        action: str,
        current_vertex: Optional[str],
        current_distance: float,
        examining_edge: Optional[Tuple[str, str, float]] = None,
        distances: Optional[Dict[str, float]] = None,
        predecessors: Optional[Dict[str, Optional[str]]] = None,
        settled_vertices: Optional[Set[str]] = None,
        heap_elements: Optional[List[Tuple[float, str]]] = None,
        message: str = "",
    ):
        self.step_number = step_number
        self.action = action  # "INIT", "EXTRACT_MIN", "RELAX", "NO_RELAX", "COMPLETE"
        self.current_vertex = current_vertex
        self.current_distance = current_distance
        self.examining_edge = examining_edge
        self.distances = dict(distances) if distances else {}
        self.predecessors = dict(predecessors) if predecessors else {}
        self.settled_vertices = set(settled_vertices) if settled_vertices else set()
        self.heap_elements = list(heap_elements) if heap_elements else []
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_number": self.step_number,
            "action": self.action,
            "current_vertex": self.current_vertex,
            "current_distance": self.current_distance,
            "examining_edge": self.examining_edge,
            "distances": {k: ("inf" if v == float("inf") else round(v, 2)) for k, v in self.distances.items()},
            "predecessors": self.predecessors,
            "settled_count": len(self.settled_vertices),
            "message": self.message,
        }


def dijkstra_min_heap(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
    track_steps: bool = False,
) -> Tuple[DijkstraResult, List[AlgorithmStep]]:
    """
    Dijkstra's Single-Source Shortest Path using Custom Indexed Min-Heap.
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)

    Parameters:
    - graph: Graph instance
    - source: start vertex key
    - target: optional destination key (early stops if target settled)
    - track_steps: whether to capture chronological steps for visualization
    """
    if source not in graph.vertices:
        raise ValueError(f"Source vertex '{source}' does not exist in graph.")
    if target is not None and target not in graph.vertices:
        raise ValueError(f"Target vertex '{target}' does not exist in graph.")

    start_perf = time.perf_counter()

    # Initialization
    all_vertices = graph.get_all_vertices()
    distances: Dict[str, float] = {v: float("inf") for v in all_vertices}
    predecessors: Dict[str, Optional[str]] = {v: None for v in all_vertices}
    settled: Set[str] = set()
    visited_order: List[str] = []

    distances[source] = 0.0

    min_heap = MinHeap()
    min_heap.insert(0.0, source)

    steps: List[AlgorithmStep] = []
    edges_examined = 0
    edge_relaxations = 0
    step_counter = 0

    if track_steps:
        step_counter += 1
        steps.append(
            AlgorithmStep(
                step_number=step_counter,
                action="INIT",
                current_vertex=source,
                current_distance=0.0,
                distances=distances,
                predecessors=predecessors,
                settled_vertices=settled,
                heap_elements=[(0.0, source)],
                message=f"Initialized Dijkstra at source '{source}'. Distance set to 0.0, all other nodes set to ∞.",
            )
        )

    # Main Dijkstra loop
    while not min_heap.is_empty():
        curr_dist, u = min_heap.extract_min()

        # If we already settled u with a shorter path, skip
        if u in settled:
            continue

        settled.add(u)
        visited_order.append(u)

        if track_steps:
            step_counter += 1
            steps.append(
                AlgorithmStep(
                    step_number=step_counter,
                    action="EXTRACT_MIN",
                    current_vertex=u,
                    current_distance=curr_dist,
                    distances=distances,
                    predecessors=predecessors,
                    settled_vertices=settled,
                    heap_elements=list(min_heap.heap),
                    message=f"Extracted node '{u}' from Min-Heap with confirmed shortest distance {curr_dist:.2f}.",
                )
            )

        # Early termination if specific destination reached
        if target is not None and u == target:
            break

        # Relax adjacent outgoing edges
        for v, weight in graph.get_neighbors(u):
            edges_examined += 1

            if v in settled:
                if track_steps:
                    step_counter += 1
                    steps.append(
                        AlgorithmStep(
                            step_number=step_counter,
                            action="SKIP_SETTLED",
                            current_vertex=u,
                            current_distance=curr_dist,
                            examining_edge=(u, v, weight),
                            distances=distances,
                            predecessors=predecessors,
                            settled_vertices=settled,
                            heap_elements=list(min_heap.heap),
                            message=f"Neighbor '{v}' is already settled. Skipping edge ({u} -> {v}, w={weight:.2f}).",
                        )
                    )
                continue

            new_dist = curr_dist + weight

            if new_dist < distances[v]:
                old_dist = distances[v]
                distances[v] = new_dist
                predecessors[v] = u
                edge_relaxations += 1

                # Update priority in custom Min-Heap (or insert if not present)
                if min_heap.contains(v):
                    min_heap.decrease_key(v, new_dist)
                else:
                    min_heap.insert(new_dist, v)

                if track_steps:
                    step_counter += 1
                    old_str = f"{old_dist:.2f}" if old_dist < float("inf") else "∞"
                    steps.append(
                        AlgorithmStep(
                            step_number=step_counter,
                            action="RELAX",
                            current_vertex=u,
                            current_distance=curr_dist,
                            examining_edge=(u, v, weight),
                            distances=distances,
                            predecessors=predecessors,
                            settled_vertices=settled,
                            heap_elements=list(min_heap.heap),
                            message=(
                                f"Relaxed edge ({u} -> {v}, w={weight:.2f}): "
                                f"Distance to '{v}' improved from {old_str} to {new_dist:.2f}."
                            ),
                        )
                    )
            else:
                if track_steps:
                    step_counter += 1
                    steps.append(
                        AlgorithmStep(
                            step_number=step_counter,
                            action="NO_RELAX",
                            current_vertex=u,
                            current_distance=curr_dist,
                            examining_edge=(u, v, weight),
                            distances=distances,
                            predecessors=predecessors,
                            settled_vertices=settled,
                            heap_elements=list(min_heap.heap),
                            message=(
                                f"Edge ({u} -> {v}, w={weight:.2f}) does not improve path to '{v}' "
                                f"(tentative: {distances[v]:.2f} <= {new_dist:.2f})."
                            ),
                        )
                    )

    elapsed_ms = (time.perf_counter() - start_perf) * 1000.0

    if track_steps:
        step_counter += 1
        steps.append(
            AlgorithmStep(
                step_number=step_counter,
                action="COMPLETE",
                current_vertex=None,
                current_distance=0.0,
                distances=distances,
                predecessors=predecessors,
                settled_vertices=settled,
                heap_elements=[],
                message=f"Dijkstra search complete. Visited {len(settled)} vertices, examined {edges_examined} edges in {elapsed_ms:.3f} ms.",
            )
        )

    heap_metrics = min_heap.get_metrics()
    result = DijkstraResult(
        algorithm_name="Min-Heap Dijkstra",
        source=source,
        distances=distances,
        predecessors=predecessors,
        visited_order=visited_order,
        execution_time_ms=elapsed_ms,
        vertices_visited_count=len(settled),
        edges_examined_count=edges_examined,
        edge_relaxations_count=edge_relaxations,
        heap_metrics=heap_metrics,
        comparisons_count=heap_metrics.get("comparisons", 0),
    )
    return result, steps


def dijkstra_unsorted_list(
    graph: Graph,
    source: str,
    target: Optional[str] = None,
) -> DijkstraResult:
    """
    Dijkstra's Shortest Path using an Unsorted List (Array) to select minimum distance vertex.
    Linear scan O(V) to find min node.
    Time Complexity: O(V^2 + E)
    Space Complexity: O(V)

    Used as the benchmark baseline against Min-Heap Dijkstra.
    """
    if source not in graph.vertices:
        raise ValueError(f"Source vertex '{source}' does not exist in graph.")
    if target is not None and target not in graph.vertices:
        raise ValueError(f"Target vertex '{target}' does not exist in graph.")

    start_perf = time.perf_counter()

    all_vertices = graph.get_all_vertices()
    distances: Dict[str, float] = {v: float("inf") for v in all_vertices}
    predecessors: Dict[str, Optional[str]] = {v: None for v in all_vertices}
    settled: Set[str] = set()
    unvisited: Set[str] = set(all_vertices)
    visited_order: List[str] = []

    distances[source] = 0.0

    edges_examined = 0
    edge_relaxations = 0
    comparisons = 0

    while unvisited:
        # Linear O(V) scan across unvisited set to find minimum tentative distance
        min_vertex: Optional[str] = None
        min_dist = float("inf")

        for v in unvisited:
            comparisons += 1
            d = distances[v]
            if d < min_dist:
                min_dist = d
                min_vertex = v

        # If min_dist is infinity, remaining nodes are in disconnected components
        if min_vertex is None or min_dist == float("inf"):
            break

        u = min_vertex
        unvisited.remove(u)
        settled.add(u)
        visited_order.append(u)

        if target is not None and u == target:
            break

        # Relax adjacent edges
        for v, weight in graph.get_neighbors(u):
            edges_examined += 1
            if v in settled:
                continue

            new_dist = min_dist + weight
            comparisons += 1
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                edge_relaxations += 1

    elapsed_ms = (time.perf_counter() - start_perf) * 1000.0

    return DijkstraResult(
        algorithm_name="Unsorted-List Dijkstra (O(V^2))",
        source=source,
        distances=distances,
        predecessors=predecessors,
        visited_order=visited_order,
        execution_time_ms=elapsed_ms,
        vertices_visited_count=len(settled),
        edges_examined_count=edges_examined,
        edge_relaxations_count=edge_relaxations,
        heap_metrics={"total_operations": 0},
        comparisons_count=comparisons,
    )
