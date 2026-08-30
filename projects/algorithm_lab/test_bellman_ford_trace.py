import unittest
from math import inf

from projects.algorithm_lab.bellman_ford_trace import bellman_ford_certificate, bellman_ford_trace, reconstruct_path


class BellmanFordTraceTests(unittest.TestCase):
    def test_negative_edge_path_and_round_invariant_are_auditable(self):
        edges = [(0, 1, 2.0), (0, 2, 5.0), (2, 1, -10.0), (1, 3, 4.0)]
        distances, parents, events = bellman_ford_trace(5, edges, source=0)
        self.assertEqual(distances, [0.0, -5.0, 5.0, -1.0, inf])
        self.assertEqual(reconstruct_path(parents, 0, 3), [0, 2, 1, 3])
        self.assertEqual(events[0].relaxed, ((0, 1, 2.0), (0, 2, 5.0)))
        self.assertEqual(events[1].relaxed, ((2, 1, -5.0), (1, 3, 6.0)))
        self.assertEqual(events[2].relaxed, ((1, 3, -1.0),))
        self.assertTrue(bellman_ford_certificate(5, edges, 0, distances, parents, events)["valid"])

        tampered_distances = list(distances)
        tampered_distances[3] = 0.0
        certificate = bellman_ford_certificate(5, edges, 0, tampered_distances, parents, events)
        self.assertFalse(certificate["labels_match_recomputed_run"])
        self.assertFalse(certificate["valid"])

    def test_unreachable_negative_cycle_does_not_change_source_distances(self):
        distances, parents, _ = bellman_ford_trace(4, [(0, 1, 3.0), (2, 3, -2.0), (3, 2, 1.0)], 0)
        self.assertEqual(distances, [0.0, 3.0, inf, inf])
        self.assertEqual(reconstruct_path(parents, 0, 3), None)

    def test_rejects_reachable_negative_cycle_and_malformed_inputs(self):
        with self.assertRaises(ValueError):
            bellman_ford_trace(3, [(0, 1, 1.0), (1, 2, -3.0), (2, 1, 1.0)], 0)
        with self.assertRaises(ValueError):
            bellman_ford_trace(2, [(0, 1, float("nan"))], 0)
        with self.assertRaises(ValueError):
            reconstruct_path([None, 2, 1], 0, 1)


if __name__ == "__main__":
    unittest.main()
