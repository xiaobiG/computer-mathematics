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


def topological_trace(graph: Graph) -> tuple[list[Node] | None, list[TopologicalEvent]]:
    """返回拓扑序和每次移除入度零顶点后的轨迹；有环时序列为 None。"""
    indegree = {node: 0 for node in graph}
    for neighbors in graph.values():
        for neighbor in neighbors:
            if neighbor not in indegree:
                raise ValueError("每个边终点必须作为 graph 的键出现")
            indegree[neighbor] += 1

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
