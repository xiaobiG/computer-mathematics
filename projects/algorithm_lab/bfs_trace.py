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


def bfs_trace_with_parents(
    graph: Graph, start: Node,
) -> tuple[dict[Node, int], dict[Node, Node | None], list[BfsEvent]]:
    """Return BFS distances, first-discovery parents, and dequeue events."""
    distances = {start: 0}
    parents: dict[Node, Node | None] = {start: None}
    queue = deque([start])
    events: list[BfsEvent] = []

    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                parents[neighbor] = node
                queue.append(neighbor)
        events.append(BfsEvent(node, distances[node], tuple(queue)))
    return distances, parents, events


def bfs_trace(graph: Graph, start: Node) -> tuple[dict[Node, int], list[BfsEvent]]:
    """Return shortest hop counts and dequeue events, preserving the original API."""
    distances, _, events = bfs_trace_with_parents(graph, start)
    return distances, events


def bfs_shortest_path_certificate(
    graph: Graph,
    start: Node,
    distances: dict[Node, int],
    parents: dict[Node, Node | None],
    events: list[BfsEvent],
) -> dict[str, bool]:
    """Check path evidence, edge lower bounds and replayed queue-layer trace.

    Parent edges prove every reported distance is attainable.  For each reached
    edge ``u -> v``, ``dist[v] <= dist[u] + 1`` proves no path can improve the
    reported labels by one more hop.  Replaying the event sequence makes the
    queue's nondecreasing-layer invariant directly inspectable.
    """
    try:
        expected_distances, expected_parents, expected_events = bfs_trace_with_parents(graph, start)
    except (TypeError, KeyError):
        return {
            "start_is_well_formed": False,
            "parent_paths_match_distances": False,
            "all_reached_edges_respect_layers": False,
            "events_replay": False,
            "valid": False,
        }
    start_is_well_formed = distances.get(start) == 0 and parents.get(start) is None
    parent_paths_match_distances = start_is_well_formed and all(
        node == start or (
            parent in distances
            and parent in graph
            and node in graph[parent]
            and distances[node] == distances[parent] + 1
        )
        for node, parent in parents.items()
    ) and set(distances) == set(parents)
    all_reached_edges_respect_layers = all(
        neighbor in distances and distances[neighbor] <= distances[node] + 1
        for node in distances
        for neighbor in graph.get(node, [])
    )
    events_replay = (
        distances == expected_distances and parents == expected_parents and events == expected_events
    )
    return {
        "start_is_well_formed": start_is_well_formed,
        "parent_paths_match_distances": parent_paths_match_distances,
        "all_reached_edges_respect_layers": all_reached_edges_respect_layers,
        "events_replay": events_replay,
        "valid": all((parent_paths_match_distances, all_reached_edges_respect_layers, events_replay)),
    }


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
