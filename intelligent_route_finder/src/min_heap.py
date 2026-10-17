"""
Min-Heap Implementation from Scratch
====================================
Designed for M.Tech DSA Project: Intelligent Route Finder
Shortest-Path Optimization Using Graph Algorithms and Min-Heap.

Features:
- Pure Python implementation without external priority queue libraries (no `heapq`).
- Node-to-index tracking (Indexed Min-Heap) for O(log V) decrease_key operations.
- Operational metrics instrumentation (comparisons, swaps, insertions, extractions, decrease-keys).
- State introspection for step-by-step algorithm visualization.
"""

from typing import Any, Dict, List, Optional, Tuple


class MinHeap:
    """
    An indexed binary Min-Heap storing (priority, item) pairs.
    Maintains a position map from item -> index in heap array to enable
    efficient O(log N) decrease_key operations.
    """

    def __init__(self):
        # Internal array of tuples: [(priority, item), ...]
        self.heap: List[Tuple[float, Any]] = []
        # Mapping from item -> index in self.heap
        self.item_to_index: Dict[Any, int] = {}

        # Performance & operation counters for DSA benchmarking
        self.insertions: int = 0
        self.extract_mins: int = 0
        self.decrease_keys: int = 0
        self.comparisons: int = 0
        self.swaps: int = 0

    def __len__(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        """Return True if heap contains no elements."""
        return len(self.heap) == 0

    def contains(self, item: Any) -> bool:
        """Check if an item currently resides in the heap."""
        return item in self.item_to_index

    def peek(self) -> Optional[Tuple[float, Any]]:
        """Return (priority, item) of the minimum element without removing it."""
        if self.is_empty():
            return None
        return self.heap[0]

    def insert(self, priority: float, item: Any) -> None:
        """
        Insert an item with given priority into the Min-Heap.
        If the item already exists and new priority is lower, performs decrease_key.
        Time Complexity: O(log N)
        """
        self.insertions += 1
        if item in self.item_to_index:
            # If already in heap, update priority if smaller
            idx = self.item_to_index[item]
            current_priority = self.heap[idx][0]
            if priority < current_priority:
                self.decrease_key(item, priority)
            return

        # Place new element at end of heap array
        index = len(self.heap)
        self.heap.append((priority, item))
        self.item_to_index[item] = index

        # Restore heap property upwards
        self._bubble_up(index)

    def extract_min(self) -> Tuple[float, Any]:
        """
        Remove and return the element with the lowest priority value.
        Time Complexity: O(log N)
        Raises IndexError if heap is empty.
        """
        if self.is_empty():
            raise IndexError("extract_min called on an empty Min-Heap.")

        self.extract_mins += 1
        min_element = self.heap[0]
        del self.item_to_index[min_element[1]]

        # If only one element was in heap, pop and return
        if len(self.heap) == 1:
            return self.heap.pop()

        # Move the last element to the root and sink it down
        last_element = self.heap.pop()
        self.heap[0] = last_element
        self.item_to_index[last_element[1]] = 0

        self._sink_down(0)
        return min_element

    def decrease_key(self, item: Any, new_priority: float) -> None:
        """
        Decrease the priority value of an existing item in the heap.
        Time Complexity: O(log N) using position mapping.
        """
        if item not in self.item_to_index:
            raise KeyError(f"Item '{item}' not found in Min-Heap.")

        idx = self.item_to_index[item]
        old_priority = self.heap[idx][0]

        if new_priority > old_priority:
            raise ValueError(
                f"New priority ({new_priority}) cannot be greater than old priority ({old_priority}) in decrease_key."
            )

        self.decrease_keys += 1
        self.heap[idx] = (new_priority, item)
        self._bubble_up(idx)

    def get_priority(self, item: Any) -> Optional[float]:
        """Get the current priority of an item in the heap."""
        if item in self.item_to_index:
            idx = self.item_to_index[item]
            return self.heap[idx][0]
        return None

    def _bubble_up(self, index: int) -> None:
        """
        Percolate element at index upward until min-heap property is satisfied:
        parent(i) <= node(i).
        """
        while index > 0:
            parent_idx = (index - 1) // 2
            self.comparisons += 1
            if self.heap[index][0] < self.heap[parent_idx][0]:
                self._swap(index, parent_idx)
                index = parent_idx
            else:
                break

    def _sink_down(self, index: int) -> None:
        """
        Percolate element at index downward until min-heap property is satisfied:
        node(i) <= left_child(i) and node(i) <= right_child(i).
        """
        size = len(self.heap)
        while True:
            left_child_idx = 2 * index + 1
            right_child_idx = 2 * index + 2
            smallest_idx = index

            if left_child_idx < size:
                self.comparisons += 1
                if self.heap[left_child_idx][0] < self.heap[smallest_idx][0]:
                    smallest_idx = left_child_idx

            if right_child_idx < size:
                self.comparisons += 1
                if self.heap[right_child_idx][0] < self.heap[smallest_idx][0]:
                    smallest_idx = right_child_idx

            if smallest_idx != index:
                self._swap(index, smallest_idx)
                index = smallest_idx
            else:
                break

    def _swap(self, i: int, j: int) -> None:
        """Swap elements at indices i and j, updating the position map."""
        self.swaps += 1
        item_i = self.heap[i][1]
        item_j = self.heap[j][1]

        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.item_to_index[item_i] = j
        self.item_to_index[item_j] = i

    def get_heap_snapshot(self) -> List[Dict[str, Any]]:
        """
        Return a copy of the current heap state for visualization.
        Contains element index, item name, priority, and parent relationship.
        """
        snapshot = []
        for idx, (priority, item) in enumerate(self.heap):
            parent_idx = (idx - 1) // 2 if idx > 0 else None
            snapshot.append({
                "index": idx,
                "item": str(item),
                "priority": round(priority, 4),
                "parent_index": parent_idx,
                "left_child_index": 2 * idx + 1 if (2 * idx + 1) < len(self.heap) else None,
                "right_child_index": 2 * idx + 2 if (2 * idx + 2) < len(self.heap) else None,
            })
        return snapshot

    def get_metrics(self) -> Dict[str, int]:
        """Return operational counters recorded during heap lifetime."""
        return {
            "insertions": self.insertions,
            "extract_mins": self.extract_mins,
            "decrease_keys": self.decrease_keys,
            "comparisons": self.comparisons,
            "swaps": self.swaps,
            "total_operations": (
                self.insertions + self.extract_mins + self.decrease_keys + self.swaps
            ),
        }
