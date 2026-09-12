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


def condensation_report(graph: Graph) -> dict[str, object]:
    """Build the SCC condensation DAG and a Kahn topological certificate.

    Component ids are local to this report.  They are deliberately not a
    canonical ordering of arbitrary hashable vertices; the certificate instead
    checks the invariant that every cross-component edge goes forward in the
    returned topological order.
    """
    components = strongly_connected_components(graph)
    component_of = {
        node: component_id
        for component_id, component in enumerate(components)
        for node in component
    }
    condensation: dict[int, set[int]] = {component_id: set() for component_id in range(len(components))}
    for source, neighbors in graph.items():
        source_component = component_of[source]
        for target in neighbors:
            target_component = component_of[target]
            if source_component != target_component:
                condensation[source_component].add(target_component)

    indegree = {component_id: 0 for component_id in condensation}
    for neighbors in condensation.values():
        for target in neighbors:
            indegree[target] += 1
    ready = [component_id for component_id in condensation if indegree[component_id] == 0]
    order = []
    while ready:
        component_id = ready.pop()
        order.append(component_id)
        for target in condensation[component_id]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)

    positions = {component_id: index for index, component_id in enumerate(order)}
    cross_edges_go_forward = len(order) == len(condensation) and all(
        positions[source] < positions[target]
        for source, neighbors in condensation.items()
        for target in neighbors
    )
    return {
        "components": components,
        "component_of": component_of,
        "condensation": condensation,
        "topological_order": order,
        "cross_edges_go_forward": cross_edges_go_forward,
        "valid": cross_edges_go_forward,
    }
