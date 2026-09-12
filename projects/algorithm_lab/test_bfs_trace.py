import unittest

from projects.algorithm_lab.bfs_trace import (
    BfsEvent,
    bfs_shortest_path_certificate,
    bfs_trace,
    bfs_trace_with_parents,
    shortest_path,
)


class BfsTraceTests(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": ["F"],
            "E": ["F"],
            "F": [],
        }

    def test_distances_are_shortest_layer_counts(self):
        distances, _ = bfs_trace(self.graph, "A")
        self.assertEqual(distances, {"A": 0, "B": 1, "C": 1, "D": 2, "E": 2, "F": 3})

    def test_events_leave_queue_in_non_decreasing_distance_order(self):
        distances, events = bfs_trace(self.graph, "A")
        processed = [event.node for event in events]
        self.assertEqual([distances[node] for node in processed], sorted(distances[node] for node in processed))

    def test_shortest_path_and_unreachable_target(self):
        self.assertEqual(shortest_path(self.graph, "A", "F"), ["A", "B", "D", "F"])
        self.assertIsNone(shortest_path(self.graph, "A", "Z"))

    def test_certificate_replays_queue_events_and_rejects_tampered_distance(self):
        distances, parents, events = bfs_trace_with_parents(self.graph, "A")
        certificate = bfs_shortest_path_certificate(self.graph, "A", distances, parents, events)
        self.assertTrue(certificate["parent_paths_match_distances"])
        self.assertTrue(certificate["all_reached_edges_respect_layers"])
        self.assertTrue(certificate["events_replay"])
        self.assertTrue(certificate["valid"])

        tampered = dict(distances)
        tampered["F"] = 2
        certificate = bfs_shortest_path_certificate(self.graph, "A", tampered, parents, events)
        self.assertFalse(certificate["parent_paths_match_distances"])
        self.assertFalse(certificate["events_replay"])
        self.assertFalse(certificate["valid"])


if __name__ == "__main__":
    unittest.main()
