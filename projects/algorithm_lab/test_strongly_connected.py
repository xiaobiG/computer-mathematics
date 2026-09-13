import copy
import unittest

from projects.algorithm_lab.strongly_connected import (
    condensation_report, condensation_report_certificate,
    scc_partition_review, strongly_connected_components,
)


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
        self.assertTrue(condensation_report_certificate(graph, report))
        altered = copy.deepcopy(report)
        altered["cross_edges_go_forward"] = False
        self.assertFalse(condensation_report_certificate(graph, altered))

    def test_direct_mutual_reachability_review_rejects_a_nonmaximal_partition(self):
        graph = {"a": ["b"], "b": []}
        correct = strongly_connected_components(graph)
        self.assertTrue(scc_partition_review(graph, correct)["valid"])

        # A single claimed component has a one-vertex condensation DAG, but
        # its vertices cannot reach each other and therefore are not one SCC.
        incorrect_merge = [{"a", "b"}]
        review = scc_partition_review(graph, incorrect_merge)
        self.assertTrue(review["partition_covers_each_vertex_once"])
        self.assertFalse(review["partition_matches_mutual_reachability"])
        self.assertFalse(review["valid"])


if __name__ == "__main__":
    unittest.main()
