import unittest

from projects.algorithm_lab.strongly_connected import condensation_report, strongly_connected_components


class StronglyConnectedTests(unittest.TestCase):
    def test_partitions_mutually_reachable_vertices(self):
        graph = {"a": ["b"], "b": ["a", "c"], "c": ["d"], "d": ["c"], "e": []}
        components = strongly_connected_components(graph)
        self.assertEqual({frozenset(component) for component in components}, {frozenset({"a", "b"}), frozenset({"c", "d"}), frozenset({"e"})})

    def test_dag_vertices_are_singletons(self):
        self.assertEqual({frozenset(component) for component in strongly_connected_components({"a": ["b"], "b": []})}, {frozenset({"a"}), frozenset({"b"})})

    def test_rejects_implicit_vertex(self):
        with self.assertRaises(ValueError):
            strongly_connected_components({"a": ["missing"]})

    def test_condensation_report_turns_cross_component_edges_into_a_dag_certificate(self):
        graph = {"a": ["b"], "b": ["a", "c"], "c": ["d"], "d": ["c"], "e": ["c"]}
        report = condensation_report(graph)
        components = report["components"]
        component_of = report["component_of"]
        assert isinstance(components, list)
        assert isinstance(component_of, dict)
        self.assertTrue(report["valid"])
        self.assertTrue(report["cross_edges_go_forward"])
        self.assertEqual(component_of["a"], component_of["b"])
        self.assertEqual(component_of["c"], component_of["d"])
        self.assertNotEqual(component_of["a"], component_of["c"])
        self.assertEqual(len(report["topological_order"]), len(components))


if __name__ == "__main__":
    unittest.main()
