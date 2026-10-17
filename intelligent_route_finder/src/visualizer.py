"""
Interactive Graph and Algorithm Visualizer
==========================================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Implements Plotly-based interactive graphics:
- Graph Network Visualizer (nodes, roads, weights, shortest path highlight)
- Algorithm Step Visualizer (node state colors: unvisited, heap frontier, active, settled)
- Binary Min-Heap Tree Structure Visualizer
- Performance & Density Comparison Charts
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import math
import plotly.graph_objects as go
from .graph import Graph


def create_network_figure(
    graph: Graph,
    shortest_path: Optional[List[str]] = None,
    current_vertex: Optional[str] = None,
    settled_vertices: Optional[Set[str]] = None,
    heap_vertices: Optional[Set[str]] = None,
    examining_edge: Optional[Tuple[str, str, float]] = None,
    distances: Optional[Dict[str, float]] = None,
    predecessors: Optional[Dict[str, Optional[str]]] = None,
    show_weights: bool = True,
    height: int = 620,
    theme: str = "dark",
) -> go.Figure:
    """
    Renders an interactive 2D visualization of the road network using Plotly.
    Highlights shortest paths, active steps, heap frontiers, and settled nodes.
    """
    graph.auto_layout_if_missing()

    # Theme palette
    is_dark = (theme == "dark")
    bg_color = "#0f172a" if is_dark else "#f8fafc"
    paper_color = "#0f172a" if is_dark else "#f8fafc"
    text_color = "#e2e8f0" if is_dark else "#1e293b"
    regular_edge_color = "rgba(148, 163, 184, 0.4)" if is_dark else "rgba(100, 116, 139, 0.4)"
    regular_edge_width = 1.8
    path_edge_color = "#10b981"  # Emerald green for optimal shortest path
    path_edge_width = 5.0
    examining_edge_color = "#f59e0b"  # Amber for currently examined edge

    shortest_path_edges = set()
    if shortest_path and len(shortest_path) >= 2:
        for i in range(len(shortest_path) - 1):
            u, v = shortest_path[i], shortest_path[i + 1]
            shortest_path_edges.add((u, v))
            shortest_path_edges.add((v, u))

    examining_set = set()
    if examining_edge:
        u, v, _ = examining_edge
        examining_set.add((u, v))
        examining_set.add((v, u))

    fig = go.Figure()

    # 1. Base Edges Trace (all non-path edges)
    edge_x = []
    edge_y = []
    mid_x = []
    mid_y = []
    mid_text = []

    for u_name, v_name, weight, road in graph.get_all_edges():
        u_v = (u_name, v_name)
        if u_v in shortest_path_edges or (v_name, u_name) in shortest_path_edges:
            continue
        if u_v in examining_set or (v_name, u_name) in examining_set:
            continue

        u_node = graph.get_vertex(u_name)
        v_node = graph.get_vertex(v_name)
        if not u_node or not v_node:
            continue

        edge_x.extend([u_node.x, v_node.x, None])
        edge_y.extend([u_node.y, v_node.y, None])

        # Midpoint for label
        mid_x.append((u_node.x + v_node.x) / 2.0)
        mid_y.append((u_node.y + v_node.y) / 2.0)
        mid_text.append(f"{weight:.1f}")

    if edge_x:
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=regular_edge_width, color=regular_edge_color),
                hoverinfo="none",
                showlegend=True,
                name="Road Connections",
            )
        )

    # 2. Currently Examining Edge (in step animation)
    if examining_edge:
        eu, ev, ew = examining_edge
        un = graph.get_vertex(eu)
        vn = graph.get_vertex(ev)
        if un and vn:
            fig.add_trace(
                go.Scatter(
                    x=[un.x, vn.x],
                    y=[un.y, vn.y],
                    mode="lines",
                    line=dict(width=4.5, color=examining_edge_color, dash="dash"),
                    hoverinfo="text",
                    hovertext=f"Evaluating Edge: {eu} → {ev} (weight={ew:.2f})",
                    showlegend=True,
                    name="Examining Edge",
                )
            )

    # 3. Shortest Path Edges Trace
    if shortest_path and len(shortest_path) >= 2:
        path_x = []
        path_y = []
        for i in range(len(shortest_path) - 1):
            u_node = graph.get_vertex(shortest_path[i])
            v_node = graph.get_vertex(shortest_path[i + 1])
            if u_node and v_node:
                path_x.extend([u_node.x, v_node.x, None])
                path_y.extend([u_node.y, v_node.y, None])

        if path_x:
            fig.add_trace(
                go.Scatter(
                    x=path_x,
                    y=path_y,
                    mode="lines",
                    line=dict(width=path_edge_width, color=path_edge_color),
                    hoverinfo="none",
                    showlegend=True,
                    name="Optimal Shortest Path",
                )
            )

    # 4. Edge Weights Midpoint Scatter (Clean badges)
    if show_weights and mid_x:
        fig.add_trace(
            go.Scatter(
                x=mid_x,
                y=mid_y,
                mode="text",
                text=mid_text,
                textposition="middle center",
                textfont=dict(
                    size=10,
                    color="#94a3b8" if is_dark else "#475569",
                    family="Courier New, monospace",
                ),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # 5. Nodes / Vertices Trace with state-aware coloring
    settled_set = settled_vertices or set()
    heap_set = heap_vertices or set()

    node_x = []
    node_y = []
    node_text = []
    node_hover = []
    node_colors = []
    node_sizes = []
    node_symbols = []
    node_border_colors = []
    node_border_widths = []

    src_name = shortest_path[0] if (shortest_path and len(shortest_path) > 0) else None
    dst_name = shortest_path[-1] if (shortest_path and len(shortest_path) > 1) else None

    for name in graph.get_all_vertices():
        v = graph.get_vertex(name)
        if not v:
            continue
        node_x.append(v.x)
        node_y.append(v.y)
        node_text.append(v.name)

        # Build informative hover text
        dist_str = "∞"
        if distances and name in distances:
            d = distances[name]
            dist_str = "0.00" if d == 0.0 else (f"{d:.2f}" if d < float("inf") else "∞ (Unreachable)")

        pred_str = predecessors.get(name, "None") if predecessors else "None"
        hover_info = (
            f"<b>{v.name}</b><br>"
            f"Category: {v.category}<br>"
            f"Degree: {graph.degree(name)}<br>"
            f"Tentative Dist: {dist_str}<br>"
            f"Predecessor: {pred_str}<br>"
            f"<i>{v.description}</i>"
        )
        node_hover.append(hover_info)

        # Determine node state color & size
        if name == current_vertex:
            # Active node currently being expanded
            node_colors.append("#f59e0b")  # Amber glow
            node_sizes.append(28)
            node_symbols.append("circle")
            node_border_colors.append("#ffffff")
            node_border_widths.append(3)
        elif name == src_name:
            # Source node
            node_colors.append("#06b6d4")  # Cyan
            node_sizes.append(26)
            node_symbols.append("star")
            node_border_colors.append("#ffffff")
            node_border_widths.append(2)
        elif name == dst_name:
            # Destination node
            node_colors.append("#ef4444")  # Bright Red
            node_sizes.append(26)
            node_symbols.append("diamond")
            node_border_colors.append("#ffffff")
            node_border_widths.append(2)
        elif shortest_path and name in shortest_path:
            # On shortest path
            node_colors.append("#10b981")  # Emerald
            node_sizes.append(24)
            node_symbols.append("circle")
            node_border_colors.append("#ffffff")
            node_border_widths.append(2)
        elif name in settled_set:
            # Settled by Dijkstra
            node_colors.append("#3b82f6")  # Blue
            node_sizes.append(20)
            node_symbols.append("circle")
            node_border_colors.append("#60a5fa")
            node_border_widths.append(1.5)
        elif name in heap_set:
            # In Min-Heap frontier
            node_colors.append("#a855f7")  # Purple
            node_sizes.append(20)
            node_symbols.append("circle")
            node_border_colors.append("#c084fc")
            node_border_widths.append(1.5)
        else:
            # Unvisited
            node_colors.append("#334155" if is_dark else "#cbd5e1")
            node_sizes.append(18)
            node_symbols.append("circle")
            node_border_colors.append("#64748b")
            node_border_widths.append(1)

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_text,
            textposition="top center",
            textfont=dict(
                size=11,
                color=text_color,
                family="Segoe UI, Roboto, Helvetica, sans-serif",
            ),
            hoverinfo="text",
            hovertext=node_hover,
            marker=dict(
                size=node_sizes,
                color=node_colors,
                symbol=node_symbols,
                line=dict(width=node_border_widths, color=node_border_colors),
            ),
            showlegend=True,
            name="Locations / Vertices",
        )
    )

    # Layout configuration
    fig.update_layout(
        title=dict(
            text=f"<b>{graph.name}</b> ({graph.vertex_count} Vertices, {graph.edge_count} Edges)",
            font=dict(size=15, color=text_color),
            x=0.02,
            y=0.98,
        ),
        paper_bgcolor=paper_color,
        plot_bgcolor=bg_color,
        hovermode="closest",
        margin=dict(b=20, l=20, r=20, t=45),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.01,
            xanchor="right",
            x=1,
            font=dict(color=text_color, size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
    )

    return fig


def create_heap_tree_figure(heap_snapshot: List[Dict[str, Any]], height: int = 340) -> go.Figure:
    """
    Renders an interactive binary tree representing the Min-Heap structure.
    Displays node array index, name, and tentative priority key.
    """
    if not heap_snapshot:
        fig = go.Figure()
        fig.add_annotation(
            text="Min-Heap is currently empty.",
            showarrow=False,
            font=dict(size=14, color="#94a3b8"),
        )
        fig.update_layout(
            height=height,
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        return fig

    # Compute binary tree node coordinates (x, y)
    positions: Dict[int, Tuple[float, float]] = {}
    max_idx = len(heap_snapshot) - 1
    max_level = int(math.log2(max_idx + 1)) if max_idx >= 0 else 0

    for item in heap_snapshot:
        idx = item["index"]
        level = int(math.log2(idx + 1))
        offset = idx - (2**level - 1)
        nodes_in_level = 2**level
        span = 100.0 / (nodes_in_level + 1)
        x = span * (offset + 1)
        y = -level * 35.0
        positions[idx] = (x, y)

    # Edge lines between parent and children
    edge_x = []
    edge_y = []
    for item in heap_snapshot:
        idx = item["index"]
        px, py = positions[idx]
        left_c = item.get("left_child_index")
        right_c = item.get("right_child_index")

        if left_c is not None and left_c in positions:
            cx, cy = positions[left_c]
            edge_x.extend([px, cx, None])
            edge_y.extend([py, cy, None])
        if right_c is not None and right_c in positions:
            cx, cy = positions[right_c]
            edge_x.extend([px, cx, None])
            edge_y.extend([py, cy, None])

    fig = go.Figure()

    if edge_x:
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(color="#475569", width=2),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Node points
    node_x = [positions[item["index"]][0] for item in heap_snapshot]
    node_y = [positions[item["index"]][1] for item in heap_snapshot]
    node_labels = [f"<b>{item['item']}</b><br>d={item['priority']}" for item in heap_snapshot]
    node_hover = [
        f"Heap Index: [{item['index']}]<br>Vertex: {item['item']}<br>Key/Dist: {item['priority']}"
        for item in heap_snapshot
    ]

    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_labels,
            textposition="top center",
            textfont=dict(size=10, color="#f1f5f9"),
            hoverinfo="text",
            hovertext=node_hover,
            marker=dict(
                size=22,
                color="#8b5cf6",
                line=dict(width=2, color="#c4b5fd"),
            ),
            showlegend=False,
        )
    )

    fig.update_layout(
        title=dict(
            text=f"<b>Binary Min-Heap Tree</b> ({len(heap_snapshot)} items)",
            font=dict(size=13, color="#e2e8f0"),
        ),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        height=height,
        margin=dict(l=15, r=15, t=35, b=15),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


def create_performance_chart(benchmark_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders empirical execution time comparison chart:
    Min-Heap Dijkstra O((V+E)logV) vs Unsorted-List Dijkstra O(V^2+E).
    """
    v_vals = [d["Vertices (V)"] for d in benchmark_data]
    heap_times = [d["Min-Heap Time (ms)"] for d in benchmark_data]
    list_times = [d["Unsorted-List Time (ms)"] for d in benchmark_data]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=v_vals,
            y=heap_times,
            mode="lines+markers",
            name="Min-Heap Dijkstra: O((V+E) log V)",
            line=dict(color="#10b981", width=3),
            marker=dict(size=8, symbol="circle"),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=v_vals,
            y=list_times,
            mode="lines+markers",
            name="Unsorted-List Dijkstra: O(V² + E)",
            line=dict(color="#ef4444", width=3, dash="dash"),
            marker=dict(size=8, symbol="diamond"),
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Execution Time vs Number of Vertices (|V|)</b>",
            font=dict(size=15, color="#e2e8f0"),
        ),
        xaxis=dict(
            title="Graph Size: Number of Vertices (|V|)",
            gridcolor="#334155",
            color="#e2e8f0",
        ),
        yaxis=dict(
            title="Execution Time (milliseconds)",
            gridcolor="#334155",
            color="#e2e8f0",
        ),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        hovermode="x unified",
        margin=dict(l=45, r=25, t=45, b=45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#e2e8f0"),
        ),
    )
    return fig


def create_density_chart(density_data: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders empirical comparison across varying edge densities for fixed |V|.
    """
    densities = [d["Density %"] for d in density_data]
    heap_times = [d["Min-Heap Time (ms)"] for d in density_data]
    list_times = [d["Unsorted-List Time (ms)"] for d in density_data]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=densities,
            y=heap_times,
            name="Min-Heap Dijkstra",
            marker_color="#10b981",
        )
    )

    fig.add_trace(
        go.Bar(
            x=densities,
            y=list_times,
            name="Unsorted-List Dijkstra",
            marker_color="#ef4444",
        )
    )

    fig.update_layout(
        title=dict(
            text="<b>Execution Time vs Graph Density (|V| Fixed)</b>",
            font=dict(size=15, color="#e2e8f0"),
        ),
        barmode="group",
        xaxis=dict(
            title="Edge Density (%)",
            gridcolor="#334155",
            color="#e2e8f0",
        ),
        yaxis=dict(
            title="Execution Time (ms)",
            gridcolor="#334155",
            color="#e2e8f0",
        ),
        paper_bgcolor="#0f172a",
        plot_bgcolor="#1e293b",
        hovermode="x unified",
        margin=dict(l=45, r=25, t=45, b=45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#e2e8f0"),
        ),
    )
    return fig
