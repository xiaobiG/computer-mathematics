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


def _validate_graph(graph: Graph, start: Node) -> None:
    """Reject incomplete adjacency maps before any traversal contract starts."""
    if start not in graph:
        raise ValueError("start must be a graph key")
    if any(neighbor not in graph for neighbors in graph.values() for neighbor in neighbors):
        raise ValueError("every neighbor must be a graph key")


def directed_cycle_report(graph: Graph, start: Node) -> dict[str, object]:
    """Return a deterministic reachable directed-cycle witness, if one exists.

    The stack stores active DFS frames.  A neighbor already coloured gray is an
    ancestor of the current frame, so its edge closes a directed cycle.  The
    returned tuple starts and ends at that ancestor; it is a witness a caller
    can check edge by edge, rather than merely a Boolean assertion.
    """
    _validate_graph(graph, start)
    color: dict[Node, str] = {start: "gray"}
    parent: dict[Node, Node | None] = {start: None}
    stack: list[tuple[Node, int]] = [(start, 0)]
    reachable: list[Node] = [start]

    while stack:
        node, next_index = stack[-1]
        if next_index == len(graph[node]):
            color[node] = "black"
            stack.pop()
            continue

        neighbor = graph[node][next_index]
        stack[-1] = (node, next_index + 1)
        neighbor_color = color.get(neighbor, "white")
        if neighbor_color == "white":
            color[neighbor] = "gray"
            parent[neighbor] = node
            reachable.append(neighbor)
            stack.append((neighbor, 0))
        elif neighbor_color == "gray":
            path_to_ancestor = [node]
            while path_to_ancestor[-1] != neighbor:
                predecessor = parent[path_to_ancestor[-1]]
                # A gray neighbor is on the active parent chain by invariant.
                if predecessor is None:
                    raise AssertionError("gray vertex must be an ancestor")
                path_to_ancestor.append(predecessor)
            cycle = tuple(reversed(path_to_ancestor)) + (neighbor,)
            return {
                "reachable": tuple(reachable),
                "back_edge": (node, neighbor),
                "cycle": cycle,
                "has_cycle": True,
            }

    return {
        "reachable": tuple(reachable),
        "back_edge": None,
        "cycle": None,
        "has_cycle": False,
    }


def directed_cycle_certificate(graph: Graph, start: Node, report: dict[str, object]) -> bool:
    """Replay the deterministic cycle search and check the reported witness."""
    try:
        return isinstance(report, dict) and report == directed_cycle_report(graph, start)
    except (AssertionError, TypeError, ValueError):
        return False
