"""记录 Kahn 拓扑排序状态，用于观察依赖如何逐步解除。"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Hashable

Node = Hashable
Graph = dict[Node, list[Node]]


@dataclass(frozen=True)
class TopologicalEvent:
    node: Node
    order_after_removal: tuple[Node, ...]
    ready_after_removal: tuple[Node, ...]


def _initial_indegrees(graph: Graph) -> dict[Node, int]:
    indegree = {node: 0 for node in graph}
    for neighbors in graph.values():
        for neighbor in neighbors:
            if neighbor not in indegree:
                raise ValueError("每个边终点必须作为 graph 的键出现")
            indegree[neighbor] += 1
    return indegree


def topological_trace(graph: Graph) -> tuple[list[Node] | None, list[TopologicalEvent]]:
    """返回拓扑序和每次移除入度零顶点后的轨迹；有环时序列为 None。"""
    indegree = _initial_indegrees(graph)

    ready = deque(node for node, degree in indegree.items() if degree == 0)
    order: list[Node] = []
    events: list[TopologicalEvent] = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for neighbor in graph[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
        events.append(TopologicalEvent(node, tuple(order), tuple(ready)))

    return (order if len(order) == len(graph) else None), events


def topological_trace_certificate(
    graph: Graph, order: list[Node] | None, events: list[TopologicalEvent],
) -> dict[str, bool]:
    """Replay Kahn's invariant and certify either an order or its cycle witness.

    When a replay exhausts ready vertices before all nodes are removed, every
    remaining vertex has positive residual indegree.  In a finite directed
    graph, following incoming edges from such a vertex must repeat, witnessing
    a directed cycle.
    """
    indegree = _initial_indegrees(graph)
    ready = deque(node for node, degree in indegree.items() if degree == 0)
    expected_order: list[Node] = []
    events_match_kahn = True
    for event in events:
        if not ready or event.node != ready.popleft():
            events_match_kahn = False
            break
        expected_order.append(event.node)
        for neighbor in graph[event.node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
        if (event.order_after_removal != tuple(expected_order)
                or event.ready_after_removal != tuple(ready)):
            events_match_kahn = False
            break
    if events_match_kahn:
        while ready:
            node = ready.popleft()
            expected_order.append(node)
            for neighbor in graph[node]:
                indegree[neighbor] -= 1
                if indegree[neighbor] == 0:
                    ready.append(neighbor)
        events_match_kahn = len(events) == len(expected_order)

    if order is None:
        residual_nodes_have_positive_indegree = (
            len(expected_order) < len(graph) and all(indegree[node] > 0 for node in set(graph) - set(expected_order))
        )
        order_respects_edges = True
        valid = events_match_kahn and residual_nodes_have_positive_indegree
    else:
        positions = {node: index for index, node in enumerate(order)}
        order_respects_edges = (
            len(order) == len(graph) == len(positions)
            and set(positions) == set(graph)
            and all(positions[source] < positions[target]
                    for source, neighbors in graph.items() for target in neighbors)
        )
        residual_nodes_have_positive_indegree = False
        valid = events_match_kahn and order == expected_order and order_respects_edges
    return {
        "events_match_kahn": events_match_kahn,
        "order_respects_edges": order_respects_edges,
        "residual_nodes_have_positive_indegree": residual_nodes_have_positive_indegree,
        "valid": valid,
    }
