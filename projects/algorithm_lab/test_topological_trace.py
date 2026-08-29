import unittest

from projects.algorithm_lab.topological_trace import topological_trace


class TopologicalTraceTests(unittest.TestCase):
    def test_order_respects_all_dependencies(self):
        graph = {"build": ["compile", "lint"], "compile": ["parse"], "lint": ["parse"], "parse": []}
        order, events = topological_trace(graph)
        self.assertIsNotNone(order)
        position = {node: index for index, node in enumerate(order)}
        self.assertTrue(all(position[source] < position[target] for source, targets in graph.items() for target in targets))
        self.assertEqual(events[-1].order_after_removal, tuple(order))

    def test_cycle_returns_none(self):
        order, events = topological_trace({"a": ["b"], "b": ["c"], "c": ["a"]})
        self.assertIsNone(order)
        self.assertEqual(events, [])

    def test_rejects_implicit_vertex(self):
        with self.assertRaises(ValueError):
            topological_trace({"a": ["missing"]})


if __name__ == "__main__":
    unittest.main()
