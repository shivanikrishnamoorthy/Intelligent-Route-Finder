# Intelligent Route Finder: Shortest-Path Optimization Using Graph Algorithms and Min-Heap

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.20%2B-3F4F75.svg)](https://plotly.com/)
[![Tests](https://img.shields.io/badge/Unit%20Tests-26%20Passing-success.svg)]()
[![Course](https://img.shields.io/badge/Academic-M.Tech%20DSA%20Project-purple.svg)]()

An interactive, production-grade Python web application developed for an **M.Tech Data Structures and Algorithms (DSA)** project. The system models realistic road, logistics, and campus networks as weighted graphs, performs single-source shortest-path optimization using **Dijkstra's Algorithm** backed by a **custom-built Indexed Min-Heap**, and provides real-time algorithmic animation and empirical benchmark analysis against an $O(V^2 + E)$ unsorted-list implementation.

---

## 🌟 Key Highlights & Academic Contributions

1. **Custom Min-Heap Built from Scratch (`min_heap.py`):**
   - Implemented without relying on Python's built-in `heapq` or standard priority queues.
   - **Position Hash Map (Indexed Min-Heap):** Maintains an internal `item_to_index` mapping updated during swaps, enabling strict $O(\log V)$ `decrease_key` operations rather than the typical $O(N)$ lookup.
   - **Operational Telemetry:** Accurately counts insertions, extractions, decrease-keys, comparisons, and array swaps for algorithmic auditing.

2. **Graph Modeling via Adjacency List (`graph.py`):**
   - Memory-efficient adjacency list: $\text{Vertex} \to [(\text{Neighbor}, \text{Weight}, \text{EdgeMetadata})]$.
   - Supports 2D spatial coordinates $(x, y)$ for accurate, topological cartesian map visualizations.
   - Enforces mathematical invariants: rejects negative edge weights ($w(u, v) \ge 0$) required for Dijkstra's greedy choice property.
   - Supports serialization to and from JSON and CSV edge lists.

3. **Dual Shortest-Path Algorithm Implementations (`dijkstra.py`):**
   - **Min-Heap Dijkstra:** Asymptotic runtime of $\mathcal{O}((V + E) \log V)$ with atomic execution step logging.
   - **Unsorted-List Dijkstra:** Baseline implementation with linear scan minimum selection running in $\mathcal{O}(V^2 + E)$.
   - Validated for strict output parity across all graph topologies.

4. **Interactive Plotly Visualization Dashboard (`visualizer.py` & `app.py`):**
   - High-contrast road network renderer with glowing shortest-path routes, node state color-coding (unvisited, frontier, active, settled), and road distance badges.
   - **Step-by-Step Playback Controller:** Slider and step buttons to inspect atomic algorithm actions (`INIT`, `EXTRACT_MIN`, `RELAX`, `SKIP_SETTLED`, `COMPLETE`).
   - **Live Binary Min-Heap Tree Diagram:** Real-time visualization of the heap's binary tree array structure.

5. **Empirical Performance Analyzer & Benchmark Engine (`benchmark.py`):**
   - Generates synthetic connected graphs with controlled vertex counts $|V|$ and edge densities $D$.
   - Executes real empirical benchmark trials (averaging multiple runs) rather than static or fabricated data.
   - Generates interactive Plotly curves comparing runtime vs $|V|$, speedup factors, comparison counts, and the impact of edge density.

6. **Comprehensive Edge Case & Resiliency Testing (`tests/`):**
   - 26 rigorous unit tests covering disconnected components, unreachable targets ($\infty$ distance), source equals destination, alternative routes, and zero-weight edges.

---

## 📁 Project Folder Structure

```
intelligent_route_finder/
│
├── src/
│   ├── __init__.py           # Package exports
│   ├── min_heap.py           # Custom Indexed Min-Heap from scratch with metrics
│   ├── graph.py              # Adjacency list graph with 2D coordinates & validation
│   ├── dijkstra.py           # Min-Heap Dijkstra, Unsorted-List Dijkstra & StepLogger
│   ├── benchmark.py          # Synthetic graph generator & empirical benchmark suite
│   ├── visualizer.py         # Plotly network map, heap tree & benchmark chart visualizer
│   └── sample_data.py        # Realistic datasets (Metro, Logistics, Campus, Disconnected)
│
├── data/
│   ├── metro_network.json    # Smart city metro transit network
│   ├── campus_network.json   # University campus pedestrian network
│   └── sample_edges.csv      # CSV edge list for custom uploads
│
├── tests/
│   ├── __init__.py
│   ├── test_min_heap.py      # Unit tests for heap operations, decrease_key, and invariants
│   ├── test_graph.py         # Unit tests for adjacency list, weights, and connectivity
│   ├── test_dijkstra.py      # Unit tests for shortest paths, parity, and edge cases
│   └── test_benchmark.py     # Unit tests for synthetic graph generation and benchmark suite
│
├── app.py                    # Production Streamlit Web Dashboard
├── requirements.txt          # Python dependencies
└── README.md                 # Complete documentation & execution guide
```

---

## 🧮 Algorithmic Complexity & Mathematical Analysis

### 1. Asymptotic Complexity Comparison

| Operation / Phase | Min-Heap Dijkstra (Implemented) | Unsorted-List Dijkstra (Baseline) | Fibonacci Heap (Theoretical) |
| :--- | :--- | :--- | :--- |
| **Initialize Distances** | $\mathcal{O}(V)$ | $\mathcal{O}(V)$ | $\mathcal{O}(V)$ |
| **Extract-Min (V times)** | $V \times \mathcal{O}(\log V) = \mathcal{O}(V \log V)$ | $V \times \mathcal{O}(V) = \mathcal{O}(V^2)$ | $V \times \mathcal{O}(\log V) = \mathcal{O}(V \log V)$ |
| **Decrease-Key / Relax (E times)** | $E \times \mathcal{O}(\log V) = \mathcal{O}(E \log V)$ | $E \times \mathcal{O}(1) = \mathcal{O}(E)$ | $E \times \mathcal{O}(1)$ (amortized) |
| **Total Time Complexity** | **$\mathbf{\mathcal{O}((V + E) \log V)}$** | **$\mathbf{\mathcal{O}(V^2 + E)}$** | **$\mathbf{\mathcal{O}(V \log V + E)}$** |
| **Auxiliary Space Complexity** | $\mathcal{O}(V + E)$ (Adjacency List + Heap) | $\mathcal{O}(V + E)$ | $\mathcal{O}(V + E)$ |

### 2. Density Crossover Analysis
- **Sparse Graphs ($E = \mathcal{O}(V)$):**
  - Min-Heap: $\mathcal{O}(V \log V)$
  - Unsorted List: $\mathcal{O}(V^2)$
  - Min-Heap achieves significant speedup proportional to $\approx \frac{V}{\log V}$.
- **Dense Graphs ($E = \Theta(V^2)$):**
  - Min-Heap: $\mathcal{O}(V^2 \log V)$
  - Unsorted List: $\mathcal{O}(V^2)$
  - When the graph approaches a complete graph ($D \to 1.0$), each relaxation incurs an $O(\log V)$ heap update, narrowing the gap with the $O(V^2)$ unsorted list.

---

## 💻 Windows & VS Code Setup and Execution

### Prerequisites
- Python 3.10 or higher installed (Tested on Python 3.13 on Windows).
- Git installed (optional).
- VS Code (Visual Studio Code).

### Step 1: Open the Project in VS Code
1. Open VS Code.
2. Select **File > Open Folder...** and select:
   ```
   C:\Users\<YOUR_USER>\Desktop\intelligent_route_finder
   ```
3. Open an integrated terminal in VS Code using ``Ctrl + ` `` (Backtick) or **Terminal > New Terminal**.

### Step 2: Create and Activate a Virtual Environment (Recommended)
In the VS Code terminal (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Unit Test Suite
Verify that all 26 algorithmic and data structure tests pass:
```powershell
python -m pytest tests -v
```
Expected output:
```
tests/test_benchmark.py::TestBenchmark::test_synthetic_graph_connected PASSED
tests/test_benchmark.py::TestBenchmark::test_benchmark_suite_execution PASSED
tests/test_dijkstra.py::TestDijkstra::test_standard_shortest_path PASSED
tests/test_dijkstra.py::TestDijkstra::test_min_heap_and_unsorted_list_parity PASSED
tests/test_dijkstra.py::TestDijkstra::test_source_equals_destination PASSED
tests/test_dijkstra.py::TestDijkstra::test_disconnected_graph_unreachable PASSED
tests/test_dijkstra.py::TestDijkstra::test_alternative_routes_optimization PASSED
tests/test_dijkstra.py::TestDijkstra::test_zero_weight_edges PASSED
tests/test_dijkstra.py::TestDijkstra::test_invalid_source_or_target PASSED
tests/test_dijkstra.py::TestDijkstra::test_step_tracking PASSED
tests/test_graph.py::TestGraph::test_vertex_addition PASSED
tests/test_graph.py::TestGraph::test_edge_addition_bidirectional PASSED
tests/test_graph.py::TestGraph::test_negative_weight_rejected PASSED
tests/test_graph.py::TestGraph::test_connectivity PASSED
tests/test_min_heap.py::TestMinHeap::test_sorted_extraction PASSED
tests/test_min_heap.py::TestMinHeap::test_decrease_key PASSED
============================= 26 passed in 0.15s ==============================
```

### Step 5: Launch the Streamlit Web Dashboard
Run the following command:
```powershell
streamlit run app.py
```
Streamlit will automatically open your default browser at:
```
http://localhost:8501
```

---

## 🖥️ Application Modules & User Guide

### 1. 📍 Route Finder
- **Source & Destination Selector:** Choose starting point and target destination.
- **Interactive Network Map:** Plotly graph displaying all vertices, road lengths, and highlighted shortest path in bright emerald green.
- **Metric Cards:** Displays exact shortest distance, number of hops, vertices visited, Min-Heap operations, and runtime in milliseconds.
- **Turn-by-Turn Itinerary:** Step-by-step navigation breakdown detailing road names, segment distances, and cumulative mileage.
- **Unreachable Detection:** Handles disconnected networks cleanly and lists all unreachable nodes.

### 2. 🎬 Step-by-Step Algorithm Visualizer
- **Chronological Slider:** Scrub through atomic algorithm iterations.
- **Node State Indicators:**
  - 🟡 **Amber:** Currently active vertex being expanded.
  - 🟣 **Purple:** Frontier nodes currently held in the Min-Heap.
  - 🔵 **Blue:** Settled vertices with finalized shortest distances.
  - ⚪ **Slate:** Unvisited vertices.
- **Live Binary Min-Heap Tree:** Plotly visualization of the complete binary heap tree with array indices and priority values.
- **Relaxation Table:** Live inspection of tentative distances $d[v]$ and predecessors $\pi[v]$.

### 3. ⚡ Performance Analyzer
- **Scalability Benchmark (Varying $|V|$):** Evaluates Min-Heap vs Unsorted-List across 10 to 300 vertices.
- **Density Benchmark (Varying $D$):** Evaluates runtime behavior across edge densities from 5% to 70%.
- **Live Execution:** Runs real algorithmic loops on synthetic connected graphs; plots empirical execution times and speedup factors.
- **CSV Data Export:** One-click download of benchmark datasets.

### 4. 🛠️ Custom Graph Builder & Network Manager
- **Interactive Forms:** Add custom vertices with $(x, y)$ coordinates and category tags; add directed or undirected weighted edges.
- **Synthetic Graph Generator:** Generate random connected graphs on demand.
- **CSV Import / Export:** Upload your own road network edge lists (`source,target,weight,road_name`).

### 5. 📚 Theory & Complexity Report
- Detailed academic documentation containing mathematical proofs, greedy choice invariants, edge relaxation mechanics, and architectural design patterns.

---

## 🧪 Edge Cases Handled

1. **Source Equals Destination:** Returns distance `0.0`, path `[Source]`, and execution time $< 0.05$ ms.
2. **Disconnected Graphs:** Unreachable nodes receive distance $\infty$, empty path, and are segregated into an alert banner.
3. **Alternative Routes:** Confirmed through unit tests that paths with smaller cumulative weights are strictly selected over routes with fewer hops or larger direct edges.
4. **Zero-Weight Edges:** Zero-weight roads ($w(u, v) = 0$) are fully supported and preserve Dijkstra correctness.
5. **Negative Weight Validation:** Input validation throws an explicit `ValueError` if any negative weight is supplied, explaining Dijkstra's precondition.
6. **Isolated Nodes:** Handled gracefully without division-by-zero or indexing exceptions.

---

## 📜 Academic Attribution

- **Project:** Intelligent Route Finder: Shortest-Path Optimization Using Graph Algorithms and Min-Heap
- **Curriculum:** M.Tech Computer Science / Data Structures & Algorithms (DSA)
- **Author:** Developed for pair-programming project submission
- **License:** MIT License
