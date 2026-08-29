"""Kosaraju 强连通分量教学实现，使用显式栈避免递归深度限制。"""

from __future__ import annotations

from typing import Hashable

Node = Hashable
Graph = dict[Node, list[Node]]


def _validate(graph: Graph) -> None:
    if any(neighbor not in graph for neighbors in graph.values() for neighbor in neighbors):
        raise ValueError("every neighbor must be a graph key")


def _finish_order(graph: Graph) -> list[Node]:
    seen, order = set(), []
    for start in graph:
        if start in seen:
            continue
        seen.add(start)
        stack = [(start, False)]
        while stack:
            node, finishing = stack.pop()
            if finishing:
                order.append(node)
            else:
                stack.append((node, True))
                for neighbor in reversed(graph[node]):
                    if neighbor not in seen:
                        seen.add(neighbor)
                        stack.append((neighbor, False))
    return order


def strongly_connected_components(graph: Graph) -> list[set[Node]]:
    """Partition a directed graph into mutual-reachability equivalence classes."""
    _validate(graph)
    reverse = {node: [] for node in graph}
    for source, neighbors in graph.items():
        for target in neighbors:
            reverse[target].append(source)
    seen, components = set(), []
    for start in reversed(_finish_order(graph)):
        if start in seen:
            continue
        component, stack = set(), [start]
        seen.add(start)
        while stack:
            node = stack.pop()
            component.add(node)
            for neighbor in reverse[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return components
