"""
Performance Benchmark Engine
============================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Compares:
1. Min-Heap Dijkstra: O((V + E) log V)
2. Unsorted-List Dijkstra: O(V^2 + E)

Generates REAL synthetic graphs with controlled sizes and densities,
executing actual benchmark runs to record empirical runtime and operation counts.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
import math
import random
import time
from .dijkstra import dijkstra_min_heap, dijkstra_unsorted_list
from .graph import Graph


def generate_random_connected_graph(
    num_vertices: int,
    density: float = 0.2,
    directed: bool = False,
    min_weight: float = 1.0,
    max_weight: float = 100.0,
    seed: Optional[int] = None,
) -> Graph:
    """
    Generate a random connected graph with specified number of vertices and approximate edge density.
    Ensures connectivity by first creating a spanning backbone (tree), then adding additional edges.
    """
    if seed is not None:
        random.seed(seed)

    if num_vertices < 1:
        raise ValueError("Graph must contain at least 1 vertex.")

    g = Graph(name=f"Synthetic Graph (V={num_vertices}, D={density:.2f})", directed=directed)

    # 1. Add vertices placed in a 2D space
    radius = 50.0 + 10.0 * math.sqrt(num_vertices)
    for i in range(num_vertices):
        name = f"V{i}"
        # Circular with small random jitter
        angle = 2.0 * math.pi * i / num_vertices
        jitter_r = random.uniform(0.85, 1.15)
        x = round((radius * jitter_r) * math.cos(angle) + 100.0, 2)
        y = round((radius * jitter_r) * math.sin(angle) + 100.0, 2)
        g.add_vertex(name, x=x, y=y, category="Node", description=f"Synthetic Vertex {i}")

    if num_vertices == 1:
        return g

    all_nodes = [f"V{i}" for i in range(num_vertices)]

    # 2. Guarantee connectivity: Create a random spanning tree
    shuffled_nodes = list(all_nodes)
    random.shuffle(shuffled_nodes)
    connected_set = [shuffled_nodes[0]]

    existing_edges = set()

    for node in shuffled_nodes[1:]:
        u = random.choice(connected_set)
        w = round(random.uniform(min_weight, max_weight), 2)
        g.add_edge(u, node, w, road_name=f"{u}-{node}", bidirectional=not directed)
        edge_key = (min(u, node), max(u, node)) if not directed else (u, node)
        existing_edges.add(edge_key)
        connected_set.append(node)

    # 3. Add remaining edges to reach target density
    max_possible_edges = num_vertices * (num_vertices - 1) if directed else (num_vertices * (num_vertices - 1)) // 2
    target_edges = max(len(existing_edges), int(max_possible_edges * density))

    attempts = 0
    max_attempts = (target_edges - len(existing_edges)) * 10 + 500

    while len(existing_edges) < target_edges and attempts < max_attempts:
        attempts += 1
        u = random.choice(all_nodes)
        v = random.choice(all_nodes)
        if u == v:
            continue
        edge_key = (min(u, v), max(u, v)) if not directed else (u, v)
        if edge_key not in existing_edges:
            w = round(random.uniform(min_weight, max_weight), 2)
            g.add_edge(u, v, w, road_name=f"{u}-{v}", bidirectional=not directed)
            existing_edges.add(edge_key)

    return g


def run_benchmark_suite(
    vertex_sizes: List[int],
    density: float = 0.2,
    runs_per_size: int = 3,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> List[Dict[str, Any]]:
    """
    Run empirical benchmarks comparing Min-Heap Dijkstra vs Unsorted-List Dijkstra
    across multiple graph sizes (|V|).
    """
    results: List[Dict[str, Any]] = []
    total_steps = len(vertex_sizes)

    for step_idx, v_count in enumerate(vertex_sizes):
        if progress_callback:
            progress_callback(step_idx + 1, total_steps, f"Testing |V| = {v_count} (Density = {density:.2f})...")

        # Generate graph
        g = generate_random_connected_graph(num_vertices=v_count, density=density, seed=42 + v_count)
        source = "V0"
        actual_e = g.edge_count

        heap_times = []
        list_times = []
        heap_comparisons = 0
        list_comparisons = 0
        heap_ops = 0

        for r in range(runs_per_size):
            # 1. Run Min-Heap Dijkstra
            res_heap, _ = dijkstra_min_heap(g, source=source, target=None, track_steps=False)
            heap_times.append(res_heap.execution_time_ms)
            heap_comparisons = res_heap.comparisons_count
            heap_ops = res_heap.heap_metrics.get("total_operations", 0)

            # 2. Run Unsorted-List Dijkstra
            res_list = dijkstra_unsorted_list(g, source=source, target=None)
            list_times.append(res_list.execution_time_ms)
            list_comparisons = res_list.comparisons_count

        avg_heap_time = sum(heap_times) / len(heap_times)
        avg_list_time = sum(list_times) / len(list_times)
        speedup = (avg_list_time / avg_heap_time) if avg_heap_time > 0 else 1.0

        # Theoretical complexity estimates (normalized)
        theoretical_heap = (v_count + actual_e) * math.log2(max(v_count, 2))
        theoretical_list = (v_count ** 2) + actual_e

        results.append({
            "Vertices (V)": v_count,
            "Edges (E)": actual_e,
            "Density": round(g.compute_density(), 3),
            "Min-Heap Time (ms)": round(avg_heap_time, 4),
            "Unsorted-List Time (ms)": round(avg_list_time, 4),
            "Speedup (List / Heap)": round(speedup, 2),
            "Min-Heap Comparisons": heap_comparisons,
            "Unsorted-List Comparisons": list_comparisons,
            "Heap Operations": heap_ops,
            "Theoretical O((V+E)logV)": round(theoretical_heap, 1),
            "Theoretical O(V^2+E)": round(theoretical_list, 1),
        })

    return results


def run_density_benchmark_suite(
    num_vertices: int = 100,
    densities: Optional[List[float]] = None,
    runs_per_density: int = 3,
    progress_callback: Optional[Callable[[int, int, str], None]] = None,
) -> List[Dict[str, Any]]:
    """
    Run empirical benchmarks comparing performance across varying graph edge densities
    for a fixed vertex count |V|.
    """
    if densities is None:
        densities = [0.05, 0.10, 0.20, 0.35, 0.50, 0.75]

    results: List[Dict[str, Any]] = []
    total_steps = len(densities)

    for step_idx, d in enumerate(densities):
        if progress_callback:
            progress_callback(step_idx + 1, total_steps, f"Testing Density = {d*100:.0f}% for |V| = {num_vertices}...")

        g = generate_random_connected_graph(num_vertices=num_vertices, density=d, seed=100 + int(d * 1000))
        source = "V0"
        actual_e = g.edge_count

        heap_times = []
        list_times = []

        for _ in range(runs_per_density):
            res_heap, _ = dijkstra_min_heap(g, source=source, target=None, track_steps=False)
            heap_times.append(res_heap.execution_time_ms)

            res_list = dijkstra_unsorted_list(g, source=source, target=None)
            list_times.append(res_list.execution_time_ms)

        avg_heap_time = sum(heap_times) / len(heap_times)
        avg_list_time = sum(list_times) / len(list_times)
        speedup = (avg_list_time / avg_heap_time) if avg_heap_time > 0 else 1.0

        results.append({
            "Density": round(d, 3),
            "Density %": f"{round(d * 100, 1)}%",
            "Vertices (V)": num_vertices,
            "Edges (E)": actual_e,
            "Min-Heap Time (ms)": round(avg_heap_time, 4),
            "Unsorted-List Time (ms)": round(avg_list_time, 4),
            "Speedup (List / Heap)": round(speedup, 2),
        })

    return results
