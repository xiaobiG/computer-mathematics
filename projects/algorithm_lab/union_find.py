"""Inspectable disjoint-set union experiments for the graph lessons."""

from __future__ import annotations


class UnionFind:
    """Maintain an insertion-only undirected connectivity partition."""

    def __init__(self, vertex_count: int):
        if not isinstance(vertex_count, int) or isinstance(vertex_count, bool) or vertex_count < 0:
            raise ValueError("vertex_count must be a non-negative integer")
        self.parent = list(range(vertex_count))
        self.size = [1] * vertex_count
        self.components = vertex_count

    def _check_vertex(self, vertex: int) -> None:
        if not isinstance(vertex, int) or isinstance(vertex, bool) or not 0 <= vertex < len(self.parent):
            raise IndexError("vertex is out of range")

    def find(self, vertex: int) -> int:
        """Return the representative and compress the observed parent path."""
        self._check_vertex(vertex)
        root = vertex
        while self.parent[root] != root:
            root = self.parent[root]
        while vertex != root:
            next_vertex = self.parent[vertex]
            self.parent[vertex] = root
            vertex = next_vertex
        return root

    def union(self, left: int, right: int) -> bool:
        """Merge two components by size; return false when the edge closes a cycle."""
        left_root, right_root = self.find(left), self.find(right)
        if left_root == right_root:
            return False
        if self.size[left_root] < self.size[right_root]:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root
        self.size[left_root] += self.size[right_root]
        self.components -= 1
        return True

    def connected(self, left: int, right: int) -> bool:
        return self.find(left) == self.find(right)


def _chain_parent_links(vertex_count: int) -> list[int]:
    if not isinstance(vertex_count, int) or isinstance(vertex_count, bool) or vertex_count < 2:
        raise ValueError("vertex_count must be an integer at least two")
    return [vertex + 1 for vertex in range(vertex_count - 1)] + [vertex_count - 1]


def _find_without_compression(parent: list[int], start: int) -> tuple[int, int]:
    current, hops = start, 0
    while parent[current] != current:
        current = parent[current]
        hops += 1
    return current, hops


def _find_with_path_compression(parent: list[int], start: int) -> tuple[int, int]:
    root, hops = _find_without_compression(parent, start)
    current = start
    while current != root:
        next_vertex = parent[current]
        parent[current] = root
        current = next_vertex
    return root, hops


def path_compression_chain_report(vertex_count: int) -> dict[str, object]:
    """Compare repeated finds on the same controlled parent chain.

    The chain deliberately isolates path compression from union-by-size.  It
    is a finite operation-count example, not a proof of the amortised inverse
    Ackermann bound for arbitrary operation sequences.
    """
    initial = _chain_parent_links(vertex_count)
    compressed_parent = initial[:]
    root, first_hops = _find_with_path_compression(compressed_parent, 0)
    compressed_root, compressed_second_hops = _find_with_path_compression(compressed_parent, 0)
    _, uncompressed_first_hops = _find_without_compression(initial, 0)
    uncompressed_root, uncompressed_second_hops = _find_without_compression(initial, 0)
    return {
        "contract": "union-find-path-compression-chain/v1",
        "vertex_count": vertex_count,
        "initial_parent": initial,
        "root": root,
        "first_find_hops": first_hops,
        "parent_after_first_compressed_find": compressed_parent,
        "compressed_second_find_hops": compressed_second_hops,
        "uncompressed_second_find_hops": uncompressed_second_hops,
        "roots_agree": root == compressed_root == uncompressed_root,
        "initial_hops_agree": first_hops == uncompressed_first_hops,
        "compression_reduces_repeated_path_hops": compressed_second_hops < uncompressed_second_hops,
        "interpretation": "controlled_chain_evidence_not_an_amortized_bound",
    }


def path_compression_chain_certificate(vertex_count: int, report: object) -> bool:
    """Replay the controlled chain report and reject changed parent links or hops."""
    if not isinstance(report, dict):
        return False
    try:
        return report == path_compression_chain_report(vertex_count)
    except (TypeError, ValueError):
        return False
