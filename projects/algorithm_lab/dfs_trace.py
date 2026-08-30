"""显式栈 DFS 轨迹：记录发现与完成时间，避免递归深度边界。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

Node = Hashable
Graph = dict[Node, list[Node]]


@dataclass(frozen=True)
class DfsEvent:
    node: Node
    phase: str
    time: int
    stack_after_event: tuple[Node, ...]


def dfs_trace(graph: Graph, start: Node) -> tuple[dict[Node, tuple[int, int]], list[DfsEvent]]:
    """Return discovery/finish times for one reachable component using an explicit stack."""
    if start not in graph:
        raise ValueError("start must be a graph key")
    if any(neighbor not in graph for neighbors in graph.values() for neighbor in neighbors):
        raise ValueError("every neighbor must be a graph key")
    times: dict[Node, list[int]] = {}
    events: list[DfsEvent] = []
    time = 0
    stack: list[tuple[Node, bool]] = [(start, False)]
    while stack:
        node, finishing = stack.pop()
        if finishing:
            time += 1
            times[node][1] = time
            events.append(DfsEvent(node, "finish", time, tuple(item[0] for item in stack)))
        elif node not in times:
            time += 1
            times[node] = [time, -1]
            stack.append((node, True))
            for neighbor in reversed(graph[node]):
                if neighbor not in times:
                    stack.append((neighbor, False))
            events.append(DfsEvent(node, "discover", time, tuple(item[0] for item in stack)))
    return {node: (pair[0], pair[1]) for node, pair in times.items()}, events


def dfs_trace_certificate(
    graph: Graph, start: Node, times: dict[Node, tuple[int, int]], events: list[DfsEvent]
) -> bool:
    """Replay the explicit-stack DFS contract without trusting its trace."""
    try:
        expected_times, expected_events = dfs_trace(graph, start)
        return times == expected_times and events == expected_events
    except (TypeError, ValueError):
        return False
