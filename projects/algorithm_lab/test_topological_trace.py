import unittest

from projects.algorithm_lab.topological_trace import TopologicalEvent, topological_trace, topological_trace_certificate


class TopologicalTraceTests(unittest.TestCase):
    def test_order_respects_all_dependencies(self):
        graph = {"build": ["compile", "lint"], "compile": ["parse"], "lint": ["parse"], "parse": []}
        order, events = topological_trace(graph)
        self.assertIsNotNone(order)
        position = {node: index for index, node in enumerate(order)}
        self.assertTrue(all(position[source] < position[target] for source, targets in graph.items() for target in targets))
        self.assertEqual(events[-1].order_after_removal, tuple(order))
        self.assertTrue(topological_trace_certificate(graph, order, events)["valid"])

    def test_cycle_returns_none(self):
        order, events = topological_trace({"a": ["b"], "b": ["c"], "c": ["a"]})
        self.assertIsNone(order)
        self.assertEqual(events, [])
        certificate = topological_trace_certificate({"a": ["b"], "b": ["c"], "c": ["a"]}, order, events)
        self.assertTrue(certificate["residual_nodes_have_positive_indegree"])
        self.assertTrue(certificate["valid"])

    def test_certificate_rejects_a_tampered_ready_queue(self):
        graph = {"a": ["b"], "b": []}
        order, events = topological_trace(graph)
        tampered = [TopologicalEvent(events[0].node, events[0].order_after_removal, ())] + events[1:]
        self.assertFalse(topological_trace_certificate(graph, order, tampered)["events_match_kahn"])
        self.assertFalse(topological_trace_certificate(graph, order, tampered)["valid"])

    def test_rejects_implicit_vertex(self):
        with self.assertRaises(ValueError):
            topological_trace({"a": ["missing"]})


if __name__ == "__main__":
    unittest.main()
