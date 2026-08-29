import unittest

from projects.algorithm_lab.strongly_connected import strongly_connected_components


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


if __name__ == "__main__":
    unittest.main()
