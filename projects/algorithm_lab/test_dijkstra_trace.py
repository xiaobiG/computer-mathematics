import unittest
from math import inf

from projects.algorithm_lab.dijkstra_trace import (
    dijkstra_trace, reconstruct_path, shortest_path_certificate,
    shortest_path_tie_certificate, shortest_path_tie_report,
)


class DijkstraTraceTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "s": [("a", 2.0), ("b", 5.0)],
            "a": [("b", 1.0), ("t", 7.0)],
            "b": [("t", 1.0)],
            "t": [],
            "isolated": [],
        }

    def test_settled_distances_and_reconstructed_path_are_shortest(self):
        distances, parents, events = dijkstra_trace(self.graph, "s")
        self.assertEqual(distances["t"], 4.0)
        self.assertEqual(reconstruct_path(parents, "t"), ["s", "a", "b", "t"])
        self.assertEqual(distances["isolated"], inf)
        self.assertIsNone(reconstruct_path(parents, "isolated"))
        self.assertEqual([event.distance for event in events], sorted(event.distance for event in events))
        self.assertTrue(shortest_path_certificate(self.graph, "s", distances, parents, events)["valid"])

    def test_certificate_rejects_a_distance_that_breaks_relaxation_and_parent_evidence(self):
        distances, parents, events = dijkstra_trace(self.graph, "s")
        distances = dict(distances)
        distances["t"] = 8.0
        certificate = shortest_path_certificate(self.graph, "s", distances, parents, events)
        self.assertFalse(certificate["all_edges_relaxed"])
        self.assertFalse(certificate["parent_paths_match_distances"])
        self.assertFalse(certificate["valid"])

    def test_certificate_rejects_a_fabricated_successful_relaxation_event(self):
        distances, parents, events = dijkstra_trace(self.graph, "s")
        tampered = list(events)
        tampered[0] = type(events[0])(events[0].node, events[0].distance, (("t", 1.0),))
        certificate = shortest_path_certificate(self.graph, "s", distances, parents, tampered)
        self.assertTrue(certificate["trace_covers_reachable"])
        self.assertFalse(certificate["events_match_algorithm_replay"])
        self.assertFalse(certificate["valid"])

    def test_rejects_negative_nonfinite_and_implicit_edges(self):
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("a", -1.0)], "a": []}, "s")
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("a", float("nan"))], "a": []}, "s")
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("missing", 1.0)]}, "s")
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("a", True)], "a": []}, "s")

    def test_equal_shortest_paths_keep_one_parent_but_report_all_tight_predecessors(self):
        graph = {"s": [("a", 1.0), ("b", 1.0)], "a": [("t", 1.0)], "b": [("t", 1.0)], "t": []}
        report = shortest_path_tie_report(graph, "s", "t")
        self.assertEqual(report["distance"], 2.0)
        self.assertEqual(report["selected_parent"], "a")
        self.assertEqual(report["selected_path"], ["s", "a", "t"])
        self.assertEqual(report["tight_predecessors"], ["a", "b"])
        self.assertTrue(report["has_multiple_shortest_predecessors"])
        self.assertTrue(shortest_path_tie_certificate(graph, "s", "t", report))
        altered = dict(report)
        altered["tight_predecessors"] = ["a"]
        self.assertFalse(shortest_path_tie_certificate(graph, "s", "t", altered))
