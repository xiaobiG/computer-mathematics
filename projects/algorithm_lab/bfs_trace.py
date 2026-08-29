"""记录 BFS 状态轨迹，用于观察队列和最短路层级。"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Hashable, Iterable

Node = Hashable
Graph = dict[Node, list[Node]]


@dataclass(frozen=True)
class BfsEvent:
    node: Node
    distance: int
    queue_after_expansion: tuple[Node, ...]


def bfs_trace(graph: Graph, start: Node) -> tuple[dict[Node, int], list[BfsEvent]]:
    """返回最短步数与每次出队后的可视化事件。"""
    distances = {start: 0}
    queue = deque([start])
    events: list[BfsEvent] = []

    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
        events.append(BfsEvent(node, distances[node], tuple(queue)))
    return distances, events


def reconstruct_path(parents: dict[Node, Node | None], target: Node) -> list[Node]:
    path: list[Node] = []
    node: Node | None = target
    while node is not None:
        path.append(node)
        node = parents[node]
    return list(reversed(path))


def shortest_path(graph: Graph, start: Node, target: Node) -> list[Node] | None:
    parents: dict[Node, Node | None] = {start: None}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node == target:
            return reconstruct_path(parents, target)
        for neighbor in graph.get(node, []):
            if neighbor not in parents:
                parents[neighbor] = node
                queue.append(neighbor)
    return None


if __name__ == "__main__":
    example: Graph = {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["F"],
        "E": ["F"],
        "F": [],
    }
    distances, events = bfs_trace(example, "A")
    for event in events:
        print(f"取出 {event.node}; 距离={event.distance}; 队列={list(event.queue_after_expansion)}")
    print(f"到 F 的最短路径: {shortest_path(example, 'A', 'F')}")
    print(f"最短步数: {distances['F']}")
