import unittest
from math import inf

from projects.algorithm_lab.dijkstra_trace import dijkstra_trace, reconstruct_path


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

    def test_rejects_negative_nonfinite_and_implicit_edges(self):
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("a", -1.0)], "a": []}, "s")
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("a", float("nan"))], "a": []}, "s")
        with self.assertRaises(ValueError):
            dijkstra_trace({"s": [("missing", 1.0)]}, "s")
