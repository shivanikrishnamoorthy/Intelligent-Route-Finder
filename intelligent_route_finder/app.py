"""
Intelligent Route Finder: Shortest-Path Optimization Using Graph Algorithms and Min-Heap
========================================================================================
M.Tech DSA Project Dashboard
Tech Stack: Python, Streamlit, Plotly, Pandas
"""

import os
import sys
import time
import pandas as pd
import streamlit as st

# Configure sys.path so modules can be imported directly
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.graph import Graph
from src.min_heap import MinHeap
from src.dijkstra import dijkstra_min_heap, dijkstra_unsorted_list
from src.benchmark import (
    generate_random_connected_graph,
    run_benchmark_suite,
    run_density_benchmark_suite,
)
from src.sample_data import get_all_sample_graphs
from src.visualizer import (
    create_network_figure,
    create_heap_tree_figure,
    create_performance_chart,
    create_density_chart,
)

# -----------------------------------------------------------------------------
# Streamlit App Configuration & Custom Theme Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Intelligent Route Finder | M.Tech DSA",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern card styling, badges, and responsive containers
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        color: #f8fafc;
    }
    .main-header h1 {
        color: #38bdf8;
        font-size: 1.85rem;
        margin-bottom: 6px;
        font-weight: 700;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        margin-right: 8px;
    }
    .badge-dsa {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .metric-card {
        background: #1e293b;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-lbl {
        font-size: 0.82rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }
    .step-box {
        background: #0f172a;
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 6px;
        margin-bottom: 12px;
        border: 1px solid #1e293b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "sample_graphs" not in st.session_state:
    st.session_state.sample_graphs = get_all_sample_graphs()

if "current_graph_name" not in st.session_state:
    st.session_state.current_graph_name = "Smart Metro Transit (14 Stations)"

if "current_graph" not in st.session_state:
    st.session_state.current_graph = st.session_state.sample_graphs[st.session_state.current_graph_name]

if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None

if "density_results" not in st.session_state:
    st.session_state.density_results = None

if "anim_steps" not in st.session_state:
    st.session_state.anim_steps = []

if "step_idx" not in st.session_state:
    st.session_state.step_idx = 0


# -----------------------------------------------------------------------------
# Header Banner
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="main-header">
        <div>
            <span class="badge-pill">M.Tech DSA Project</span>
            <span class="badge-dsa">Min-Heap & Graph Algorithms</span>
        </div>
        <h1>Intelligent Route Finder</h1>
        <p style="margin: 0; color: #94a3b8; font-size: 0.95rem;">
            Shortest-Path Optimization Using Custom Min-Heap, Adjacency List Graphs,
            Interactive Plotly Visualization, and Empirical O((V+E) log V) vs O(V² + E) Benchmarking.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Sidebar Navigation & Network Selector
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Project Controls")

    # Network selector
    sample_names = list(st.session_state.sample_graphs.keys()) + ["Custom Graph / Builder"]
    selected_name = st.selectbox(
        "Select Road Network:",
        options=sample_names,
        index=0 if st.session_state.current_graph_name not in sample_names else sample_names.index(st.session_state.current_graph_name),
    )

    if selected_name != "Custom Graph / Builder":
        if selected_name != st.session_state.current_graph_name:
            st.session_state.current_graph_name = selected_name
            st.session_state.current_graph = st.session_state.sample_graphs[selected_name]
            st.session_state.anim_steps = []
            st.session_state.step_idx = 0
            st.rerun()

    current_g: Graph = st.session_state.current_graph

    st.markdown("---")
    st.subheader("📊 Network Topology")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        st.metric("Vertices (|V|)", current_g.vertex_count)
        st.metric("Density", f"{current_g.compute_density():.3f}")
    with col_sb2:
        st.metric("Edges (|E|)", current_g.edge_count)
        connected_str = "Yes ✅" if current_g.is_connected() else "No (Partitioned) ⚠️"
        st.metric("Connected", connected_str)

    st.markdown("---")
    navigation = st.radio(
        "Navigation Sections:",
        [
            "📍 Route Finder",
            "🎬 Step-by-Step Visualizer",
            "⚡ Performance Benchmark",
            "🛠️ Custom Graph Builder",
            "📚 Theory & Complexity",
        ],
    )

    st.markdown("---")
    st.caption("Developed for M.Tech Computer Science / Data Structures & Algorithms.")


# =============================================================================
# SECTION 1: 📍 ROUTE FINDER
# =============================================================================
if navigation == "📍 Route Finder":
    st.subheader("📍 Single-Source Shortest Path Optimization")
    st.write(
        "Find the optimal shortest route between any two locations using Dijkstra's algorithm "
        "powered by our scratch-built Indexed Min-Heap."
    )

    vertices = current_g.get_all_vertices()
    if not vertices:
        st.warning("Current graph contains no vertices. Please add vertices in the Custom Graph Builder.")
        st.stop()

    # Route selection inputs
    col_sel1, col_sel2, col_sel3 = st.columns([3, 3, 2])
    with col_sel1:
        source = st.selectbox(
            "Source Location (Start):",
            options=vertices,
            index=0,
            key="rf_source",
        )
    with col_sel2:
        default_target_idx = min(1, len(vertices) - 1)
        target = st.selectbox(
            "Destination Location (Target):",
            options=vertices,
            index=default_target_idx,
            key="rf_target",
        )
    with col_sel3:
        st.write("")
        st.write("")
        calculate_btn = st.button("🚀 Find Shortest Path", use_container_width=True, type="primary")

    # Run Dijkstra
    result, _ = dijkstra_min_heap(current_g, source=source, target=target, track_steps=False)
    shortest_path = result.get_path(target)
    is_reachable = result.is_reachable(target)
    total_distance = result.get_distance(target)

    # Metrics Row
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        if is_reachable:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-val">{total_distance:.2f}</div>
                <div class="metric-lbl">Shortest Distance</div></div>""",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-val" style="color: #ef4444;">∞</div>
                <div class="metric-lbl">Unreachable</div></div>""",
                unsafe_allow_html=True,
            )
    with m_col2:
        hop_count = len(shortest_path) - 1 if is_reachable and len(shortest_path) > 1 else 0
        st.markdown(
            f"""<div class="metric-card"><div class="metric-val">{hop_count}</div>
            <div class="metric-lbl">Road Segments / Hops</div></div>""",
            unsafe_allow_html=True,
        )
    with m_col3:
        st.markdown(
            f"""<div class="metric-card"><div class="metric-val">{result.vertices_visited_count}</div>
            <div class="metric-lbl">Nodes Settled</div></div>""",
            unsafe_allow_html=True,
        )
    with m_col4:
        st.markdown(
            f"""<div class="metric-card"><div class="metric-val">{result.heap_metrics.get('total_operations', 0)}</div>
            <div class="metric-lbl">Min-Heap Operations</div></div>""",
            unsafe_allow_html=True,
        )
    with m_col5:
        st.markdown(
            f"""<div class="metric-card"><div class="metric-val">{result.execution_time_ms:.3f} ms</div>
            <div class="metric-lbl">Execution Time</div></div>""",
            unsafe_allow_html=True,
        )

    st.write("")

    # Route Result Banner
    if source == target:
        st.info(f"Source and Destination are the same vertex ('{source}'). Distance = 0.00.")
    elif is_reachable:
        path_str = " ➔ ".join([f"**{node}**" for node in shortest_path])
        st.success(f"**Optimal Shortest Path Found ({total_distance:.2f} units):** {path_str}")
    else:
        st.error(
            f"**No Path Exists!** Destination **'{target}'** cannot be reached from **'{source}'**. "
            f"Vertices lie in disconnected graph components."
        )

    # Visualization
    fig_graph = create_network_figure(
        graph=current_g,
        shortest_path=shortest_path if is_reachable else None,
        distances=result.distances,
        predecessors=result.predecessors,
        show_weights=True,
        height=620,
    )
    st.plotly_chart(fig_graph, use_container_width=True)

    # Detailed Itinerary and Distance Table in Tabs
    tab_itin, tab_dist, tab_unreachable = st.tabs(["📋 Turn-by-Turn Itinerary", "📊 All Node Distances", "⚠️ Unreachable Vertices"])

    with tab_itin:
        if is_reachable and len(shortest_path) > 1:
            itinerary_rows = []
            cum_dist = 0.0
            for i in range(len(shortest_path) - 1):
                u = shortest_path[i]
                v = shortest_path[i + 1]
                # find edge weight and road name
                edge_weight = 0.0
                road_name = f"{u} to {v}"
                for nbr, w, edge_obj in current_g.adj.get(u, []):
                    if nbr == v:
                        edge_weight = w
                        road_name = edge_obj.road_name
                        break
                cum_dist += edge_weight
                itinerary_rows.append({
                    "Step": i + 1,
                    "From Location": u,
                    "To Location": v,
                    "Road / Transit Segment": road_name,
                    "Segment Distance": round(edge_weight, 2),
                    "Cumulative Distance": round(cum_dist, 2),
                })
            df_itin = pd.DataFrame(itinerary_rows)
            st.dataframe(df_itin, use_container_width=True, hide_index=True)
        elif source == target:
            st.info("Already at destination.")
        else:
            st.warning("No itinerary available for unreachable destination.")

    with tab_dist:
        dist_records = []
        for v in sorted(current_g.get_all_vertices()):
            d = result.distances.get(v, float("inf"))
            pred = result.predecessors.get(v)
            reachable = (d < float("inf"))
            dist_records.append({
                "Vertex": v,
                "Shortest Distance": f"{d:.2f}" if reachable else "∞ (Unreachable)",
                "Predecessor Node": pred if pred else ("(Source Root)" if v == source else "None"),
                "Status": "Settled & Reachable" if reachable else "Unreachable",
                "Path from Source": " ➔ ".join(result.get_path(v)) if reachable else "None",
            })
        st.dataframe(pd.DataFrame(dist_records), use_container_width=True, hide_index=True)

    with tab_unreachable:
        unreach = result.get_unreachable_vertices()
        if unreach:
            st.error(f"The following {len(unreach)} location(s) cannot be reached from '{source}':")
            st.write(", ".join([f"`{node}`" for node in unreach]))
        else:
            st.success("All vertices in this network are reachable from the selected source.")


# =============================================================================
# SECTION 2: 🎬 ALGORITHM STEP-BY-STEP VISUALIZER
# =============================================================================
elif navigation == "🎬 Step-by-Step Visualizer":
    st.subheader("🎬 Step-by-Step Algorithm Execution Visualizer")
    st.write(
        "Inspect the internal mechanics of Dijkstra's algorithm. Watch the **Indexed Min-Heap** "
        "manage the priority frontier, track node relaxation, and visualize settled states in real-time."
    )

    vertices = current_g.get_all_vertices()
    col_v1, col_v2, col_v3 = st.columns([3, 3, 2])
    with col_v1:
        sim_source = st.selectbox("Execution Source:", options=vertices, index=0, key="sim_src")
    with col_v2:
        sim_target = st.selectbox(
            "Target (Optional / Early Stop):",
            options=["None (Full Graph Search)"] + vertices,
            index=0,
            key="sim_dst",
        )
        target_param = None if sim_target.startswith("None") else sim_target
    with col_v3:
        st.write("")
        st.write("")
        start_sim = st.button("▶️ Generate Trace", type="primary", use_container_width=True)

    if start_sim or not st.session_state.anim_steps:
        with st.spinner("Recording algorithmic trace..."):
            _, steps = dijkstra_min_heap(current_g, source=sim_source, target=target_param, track_steps=True)
            st.session_state.anim_steps = steps
            st.session_state.step_idx = 0

    steps = st.session_state.anim_steps
    if not steps:
        st.warning("No trace steps available. Click 'Generate Trace'.")
        st.stop()

    # Step slider controls
    total_steps = len(steps)
    step_slider = st.slider(
        "Algorithm Execution Timeline (Step):",
        min_value=1,
        max_value=total_steps,
        value=st.session_state.step_idx + 1,
        key="timeline_slider",
    )
    st.session_state.step_idx = step_slider - 1
    curr_step = steps[st.session_state.step_idx]

    # Step navigation buttons
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 2, 2])
    with col_btn1:
        if st.button("⏮️ Prev", use_container_width=True) and st.session_state.step_idx > 0:
            st.session_state.step_idx -= 1
            st.rerun()
    with col_btn2:
        if st.button("Next ⏭️", use_container_width=True) and st.session_state.step_idx < total_steps - 1:
            st.session_state.step_idx += 1
            st.rerun()
    with col_btn3:
        st.write(f"**Step {st.session_state.step_idx + 1} of {total_steps}**")
    with col_btn4:
        action_color = {
            "INIT": "#38bdf8",
            "EXTRACT_MIN": "#f59e0b",
            "RELAX": "#10b981",
            "NO_RELAX": "#94a3b8",
            "SKIP_SETTLED": "#64748b",
            "COMPLETE": "#a855f7",
        }.get(curr_step.action, "#38bdf8")
        st.markdown(
            f"""<span style="background:{action_color}; color:#ffffff; padding:4px 10px; border-radius:6px; font-weight:600; font-size:0.85rem;">
            ACTION: {curr_step.action}</span>""",
            unsafe_allow_html=True,
        )

    # Step explanation message
    st.markdown(
        f"""<div class="step-box">
            <b>Algorithmic Action Log:</b><br>{curr_step.message}
        </div>""",
        unsafe_allow_html=True,
    )

    # Visualizer layout: Graph visualizer + Min-Heap binary tree
    col_vis1, col_vis2 = st.columns([3, 2])

    with col_vis1:
        heap_nodes = {item[1] for item in curr_step.heap_elements}
        fig_step = create_network_figure(
            graph=current_g,
            shortest_path=None,
            current_vertex=curr_step.current_vertex,
            settled_vertices=curr_step.settled_vertices,
            heap_vertices=heap_nodes,
            examining_edge=curr_step.examining_edge,
            distances=curr_step.distances,
            predecessors=curr_step.predecessors,
            show_weights=True,
            height=580,
        )
        st.plotly_chart(fig_step, use_container_width=True)

    with col_vis2:
        # Heap snapshot
        heap_items = []
        for idx, (p, item) in enumerate(curr_step.heap_elements):
            heap_items.append({
                "index": idx,
                "item": str(item),
                "priority": round(p, 2),
                "left_child_index": 2 * idx + 1 if 2 * idx + 1 < len(curr_step.heap_elements) else None,
                "right_child_index": 2 * idx + 2 if 2 * idx + 2 < len(curr_step.heap_elements) else None,
            })
        fig_heap = create_heap_tree_figure(heap_items, height=320)
        st.plotly_chart(fig_heap, use_container_width=True)

        st.markdown("**Tentative Distances State:**")
        step_dist_data = [
            {
                "Node": v,
                "Dist": f"{curr_step.distances[v]:.2f}" if curr_step.distances.get(v, float("inf")) < float("inf") else "∞",
                "Pred": curr_step.predecessors.get(v) or "-",
                "Status": "Settled" if v in curr_step.settled_vertices else ("In Heap" if v in heap_nodes else "Unvisited"),
            }
            for v in sorted(current_g.get_all_vertices())
        ]
        st.dataframe(pd.DataFrame(step_dist_data), height=220, use_container_width=True, hide_index=True)


# =============================================================================
# SECTION 3: ⚡ PERFORMANCE BENCHMARK
# =============================================================================
elif navigation == "⚡ Performance Benchmark":
    st.subheader("⚡ Performance Analyzer: Min-Heap vs Unsorted-List Dijkstra")
    st.write(
        r"Conduct live, empirical benchmark evaluations comparing the asymptotic efficiency "
        r"of our **Indexed Min-Heap Dijkstra ($O((V + E) \log V)$)** against an **Unsorted-List Dijkstra ($O(V^2 + E)$)**. "
        r"Benchmarks generate real random connected networks and record actual execution runtimes and operations."
    )

    tab_size, tab_density = st.tabs(["📈 Benchmark 1: Scaling Graph Size (|V|)", "📊 Benchmark 2: Impact of Edge Density"])

    with tab_size:
        st.markdown("#### Experiment A: Execution Time vs Number of Vertices (|V|)")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            sizes_option = st.multiselect(
                "Select Graph Sizes (|V|):",
                options=[10, 25, 50, 75, 100, 150, 200, 300],
                default=[10, 25, 50, 100, 150, 200],
            )
        with col_p2:
            density_val = st.slider("Fixed Edge Density:", min_value=0.05, max_value=0.60, value=0.15, step=0.05)
        with col_p3:
            repeats = st.slider("Runs per Size (Averaging):", min_value=1, max_value=5, value=3)

        if st.button("🚀 Run Live Scalability Benchmark", type="primary"):
            if not sizes_option:
                st.error("Please select at least one graph size.")
            else:
                prog_bar = st.progress(0.0)
                prog_text = st.empty()

                def update_prog(curr, total, msg):
                    prog_bar.progress(curr / total)
                    prog_text.text(msg)

                with st.spinner("Generating graphs and benchmarking algorithms..."):
                    bench_res = run_benchmark_suite(
                        vertex_sizes=sorted(sizes_option),
                        density=density_val,
                        runs_per_size=repeats,
                        progress_callback=update_prog,
                    )
                    st.session_state.benchmark_results = bench_res
                    prog_bar.empty()
                    prog_text.empty()

        if st.session_state.benchmark_results:
            bench_df = pd.DataFrame(st.session_state.benchmark_results)
            col_b1, col_b2 = st.columns([3, 2])
            with col_b1:
                fig_perf = create_performance_chart(st.session_state.benchmark_results)
                st.plotly_chart(fig_perf, use_container_width=True)
            with col_b2:
                # Speedup metric chart
                fig_speedup = go.Figure()
                fig_speedup.add_trace(
                    go.Bar(
                        x=bench_df["Vertices (V)"],
                        y=bench_df["Speedup (List / Heap)"],
                        marker_color="#38bdf8",
                        name="Speedup Factor",
                    )
                )
                fig_speedup.update_layout(
                    title="<b>Speedup Factor: List Time / Heap Time</b>",
                    xaxis_title="Vertices (|V|)",
                    yaxis_title="Speedup (x Times Faster)",
                    paper_bgcolor="#0f172a",
                    plot_bgcolor="#1e293b",
                    font=dict(color="#e2e8f0"),
                    margin=dict(l=40, r=20, t=40, b=40),
                )
                st.plotly_chart(fig_speedup, use_container_width=True)

            st.markdown("##### 📋 Empirical Performance Data Table")
            st.dataframe(bench_df, use_container_width=True, hide_index=True)

            # CSV Download
            csv_data = bench_df.to_csv(index=False)
            st.download_button(
                "📥 Export Benchmark CSV",
                data=csv_data,
                file_name="dijkstra_scalability_benchmark.csv",
                mime="text/csv",
            )

    with tab_density:
        st.markdown("#### Experiment B: Execution Time vs Edge Density (Fixed |V|)")
        st.write(
            r"In sparse graphs ($E = O(V)$), Min-Heap Dijkstra achieves optimal performance $O(V \log V)$. "
            r"As edge density approaches $1.0$ (complete graph $E \approx V^2$), the frequency of `decrease_key` "
            r"operations grows to $O(V^2 \log V)$, demonstrating why Fibonacci heaps or unsorted arrays become competitive."
        )

        col_d1, col_d2 = st.columns(2)
        with col_d1:
            fixed_v = st.slider("Fixed Vertex Count (|V|):", min_value=40, max_value=200, value=80, step=20)
        with col_d2:
            st.write("")
            run_density_btn = st.button("🚀 Run Live Density Benchmark", type="primary")

        if run_density_btn:
            prog_bar_d = st.progress(0.0)
            prog_text_d = st.empty()

            def update_prog_d(curr, total, msg):
                prog_bar_d.progress(curr / total)
                prog_text_d.text(msg)

            with st.spinner(f"Evaluating varying densities on |V|={fixed_v}..."):
                dens_res = run_density_benchmark_suite(
                    num_vertices=fixed_v,
                    densities=[0.05, 0.10, 0.20, 0.35, 0.50, 0.70],
                    runs_per_density=3,
                    progress_callback=update_prog_d,
                )
                st.session_state.density_results = dens_res
                prog_bar_d.empty()
                prog_text_d.empty()

        if st.session_state.density_results:
            fig_density = create_density_chart(st.session_state.density_results)
            st.plotly_chart(fig_density, use_container_width=True)

            dens_df = pd.DataFrame(st.session_state.density_results)
            st.dataframe(dens_df, use_container_width=True, hide_index=True)


# =============================================================================
# SECTION 4: 🛠️ CUSTOM GRAPH BUILDER & DATA MANAGER
# =============================================================================
elif navigation == "🛠️ Custom Graph Builder":
    st.subheader("🛠️ Custom Graph Builder & Network Manager")
    st.write(
        "Design custom road networks, inject test vertices and weighted edges, "
        "upload CSV edge lists, or generate synthetic topologies with controlled properties."
    )

    tab_add, tab_synth, tab_csv = st.tabs(["➕ Add Vertices & Edges", "🎲 Generate Synthetic Graph", "📁 CSV Import / Export"])

    with tab_add:
        col_va, col_ea = st.columns(2)

        with col_va:
            st.markdown("##### Add / Update Vertex")
            with st.form("vertex_form"):
                v_name = st.text_input("Vertex Name / Identifier (e.g., Station 9):")
                v_x = st.number_input("X Coordinate (for map rendering):", value=50.0, step=5.0)
                v_y = st.number_input("Y Coordinate (for map rendering):", value=50.0, step=5.0)
                v_cat = st.selectbox("Category:", ["Location", "Commercial", "Residential", "Industrial", "Transit Hub"])
                v_desc = st.text_input("Description / Notes:", value="")
                submit_v = st.form_submit_button("Add Vertex")

                if submit_v:
                    if not v_name.strip():
                        st.error("Vertex name cannot be empty.")
                    else:
                        current_g.add_vertex(v_name.strip(), x=v_x, y=v_y, category=v_cat, description=v_desc)
                        st.success(f"Vertex '{v_name}' successfully added/updated.")
                        st.rerun()

        with col_ea:
            st.markdown("##### Add Weighted Edge (Road)")
            all_v = current_g.get_all_vertices()
            if len(all_v) < 2:
                st.info("Add at least 2 vertices to create edges.")
            else:
                with st.form("edge_form"):
                    e_src = st.selectbox("Source Vertex:", options=all_v, index=0)
                    e_dst = st.selectbox("Destination Vertex:", options=all_v, index=min(1, len(all_v) - 1))
                    e_w = st.number_input("Edge Weight (Distance/Time ≥ 0):", min_value=0.0, value=10.0, step=1.0)
                    e_road = st.text_input("Road Name (Optional):", value=f"{e_src}-{e_dst}")
                    e_bidir = st.checkbox("Bidirectional (Undirected)", value=True)
                    submit_e = st.form_submit_button("Add Edge")

                    if submit_e:
                        if e_src == e_dst:
                            st.warning("Self-loops are omitted in standard road routing.")
                        else:
                            current_g.add_edge(e_src, e_dst, weight=e_w, road_name=e_road, bidirectional=e_bidir)
                            st.success(f"Edge ({e_src} ↔ {e_dst}, weight={e_w}) added successfully.")
                            st.rerun()

    with tab_synth:
        st.markdown("##### Generate Random Benchmark Graph")
        col_sg1, col_sg2, col_sg3 = st.columns(3)
        with col_sg1:
            n_vertices = st.slider("Number of Vertices (|V|):", min_value=5, max_value=60, value=15)
        with col_sg2:
            n_density = st.slider("Target Edge Density:", min_value=0.1, max_value=0.6, value=0.25, step=0.05)
        with col_sg3:
            st.write("")
            st.write("")
            gen_btn = st.button("🎲 Generate & Load Graph", type="primary")

        if gen_btn:
            new_graph = generate_random_connected_graph(num_vertices=n_vertices, density=n_density)
            st.session_state.current_graph = new_graph
            st.session_state.current_graph_name = f"Custom Synthetic (V={n_vertices}, D={n_density:.2f})"
            st.success(f"Generated new connected graph with {new_graph.vertex_count} vertices and {new_graph.edge_count} edges.")
            st.rerun()

    with tab_csv:
        st.markdown("##### Upload Edge List (CSV)")
        st.write("Format: `source,target,weight,road_name`")
        uploaded_file = st.file_uploader("Choose CSV file", type=["csv"])
        if uploaded_file is not None:
            csv_str = uploaded_file.getvalue().decode("utf-8")
            try:
                imported_g = Graph.from_csv_edge_list(csv_str, name="Uploaded Network")
                st.session_state.current_graph = imported_g
                st.session_state.current_graph_name = "Uploaded CSV Network"
                st.success(f"Successfully loaded {imported_g.vertex_count} vertices and {imported_g.edge_count} edges!")
                st.rerun()
            except Exception as ex:
                st.error(f"Error parsing CSV: {ex}")

        st.markdown("---")
        st.markdown("##### Download Current Network as CSV")
        current_csv = current_g.to_csv_edge_list()
        st.download_button(
            "📥 Download CSV Edge List",
            data=current_csv,
            file_name=f"{current_g.name.lower().replace(' ', '_')}_edges.csv",
            mime="text/csv",
        )

    # Current Graph Overview Map
    st.markdown("---")
    st.markdown(f"#### Current Graph Preview: **{current_g.name}**")
    fig_preview = create_network_figure(graph=current_g, height=520)
    st.plotly_chart(fig_preview, use_container_width=True)


# =============================================================================
# SECTION 5: 📚 THEORY & COMPLEXITY (M.TECH REPORT)
# =============================================================================
elif navigation == "📚 Theory & Complexity":
    st.subheader("📚 Algorithmic Theory, Mathematical Formulations & Complexity")
    st.write(
        "Complete academic documentation for M.Tech DSA evaluation. "
        "Details mathematical invariants, time/space complexity derivations, and data structure mechanics."
    )

    t1, t2, t3, t4 = st.tabs(["1. Dijkstra's Algorithm", "2. Custom Min-Heap", "3. Asymptotic Analysis", "4. Project Architecture"])

    with t1:
        st.markdown(
            r"""
            ### 1. Mathematical Formulation of Dijkstra's Algorithm
            Dijkstra's algorithm solves the **Single-Source Shortest Path (SSSP)** problem on a weighted graph
            $G = (V, E)$ with non-negative edge weight function $w: E \to \mathbb{R}_{\ge 0}$.

            #### Core Invariant & Greedy Choice:
            At each iteration, the algorithm settles a vertex $u \in V \setminus S$ whose tentative distance
            $d[u] = \min_{v \notin S} d[v]$ is minimal. Because all edge weights are non-negative ($w(u,v) \ge 0$),
            no future relaxation through unvisited vertices can produce a shorter path to $u$.

            #### Edge Relaxation Invariant:
            For any directed road $(u, v) \in E$:
            $$\text{If } d[u] + w(u, v) < d[v], \quad \text{then } d[v] \leftarrow d[u] + w(u, v), \; \pi[v] \leftarrow u$$

            #### Proof of Non-Negative Requirement:
            If negative edge weights $w(u, v) < 0$ exist, the greedy invariant is violated because settling a vertex
            early does not guarantee its distance is minimal. For negative weights, the **Bellman-Ford algorithm**
            ($O(VE)$) or SPFA must be utilized.
            """
        )

    with t2:
        st.markdown(
            r"""
            ### 2. Custom Indexed Min-Heap Architecture
            A standard binary min-heap satisfies the **Heap-Order Property**:
            $$\forall i > 0, \quad \text{heap}[\text{parent}(i)] \le \text{heap}[i]$$
            where parent index is $\lfloor (i - 1) / 2 \rfloor$.

            #### Why an "Indexed" Min-Heap?
            In standard priority queues without positional indexing, the `decrease_key` operation requires an $O(N)$
            linear search to locate the element prior to percolating upward.
            
            Our implementation maintains an internal hash map:
            $$\text{item\_to\_index}: \text{Vertex} \to \text{Index in heap array}$$
            Every time two nodes swap positions in `_swap(i, j)`, the dictionary positions are updated in $O(1)$ time:
            - **Insert:** $O(\log V)$
            - **Extract-Min:** $O(\log V)$
            - **Decrease-Key:** $O(\log V)$ (strict logarithmic bound)
            - **Peek:** $O(1)$
            """
        )

    with t3:
        st.markdown(
            r"""
            ### 3. Detailed Asymptotic Complexity Comparison

            | Metric | Min-Heap Dijkstra (Implemented) | Unsorted-List Dijkstra (Baseline) | Fibonacci Heap (Theoretical) |
            | :--- | :--- | :--- | :--- |
            | **Find / Extract Min** | $V \times O(\log V) = O(V \log V)$ | $V \times O(V) = O(V^2)$ | $V \times O(\log V) = O(V \log V)$ |
            | **Edge Relaxations** | $E \times O(\log V) = O(E \log V)$ | $E \times O(1) = O(E)$ | $E \times O(1)$ (amortized) |
            | **Total Time Complexity** | **$O((V + E) \log V)$** | **$O(V^2 + E)$** | **$O(V \log V + E)$** |
            | **Space Complexity** | $O(V + E)$ (Adjacency List + Heap) | $O(V + E)$ | $O(V + E)$ |

            #### The Density Crossover Analysis:
            - **Sparse Graphs ($E = O(V)$):**
              - Min-Heap: $O(V \log V)$
              - Unsorted List: $O(V^2)$
              - **Min-Heap is asymptotically superior by a factor of $\approx V / \log V$.**
            - **Dense Graphs ($E = \Theta(V^2)$):**
              - Min-Heap: $O(V^2 \log V)$
              - Unsorted List: $O(V^2)$
              - In extremely dense networks where $E \approx V^2$, the overhead of $O(\log V)$ per decrease-key makes the unsorted list or Fibonacci heap perform competitively.
            """
        )

    with t4:
        st.markdown(
            """
            ### 4. Software Architecture & Design Patterns
            The application follows clean object-oriented design and separation of concerns:

            ```
            intelligent_route_finder/
            ├── src/
            │   ├── min_heap.py      <- Custom Indexed Min-Heap with operational telemetry
            │   ├── graph.py         <- Adjacency list, 2D coordinates, non-negative validation
            │   ├── dijkstra.py      <- SSSP solver with step-by-step trace capture
            │   ├── benchmark.py     <- Synthetic connected graph generation & timing engine
            │   ├── visualizer.py    <- Interactive Plotly network & heap tree visualizer
            │   └── sample_data.py   <- Predefined realistic transit & campus networks
            ├── tests/
            │   ├── test_min_heap.py <- Invariant, decrease-key, and edge-case unit tests
            │   ├── test_graph.py    <- Adjacency, connectivity, and serialization tests
            │   ├── test_dijkstra.py <- Parity, disconnected, and 0-weight tests
            │   └── test_benchmark.py<- Synthetic graph generation & benchmark tests
            ├── app.py               <- Streamlit multi-tab production dashboard
            ├── requirements.txt     <- Pinned runtime dependencies
            └── README.md            <- Setup instructions, VS Code guide, and documentation
            ```
            """
        )
