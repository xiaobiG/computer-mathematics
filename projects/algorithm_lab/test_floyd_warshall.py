import unittest
from math import inf

from projects.algorithm_lab.floyd_warshall import (
    FloydWarshallEvent, floyd_warshall, floyd_warshall_path_certificate,
    floyd_warshall_trace, floyd_warshall_trace_certificate, floyd_warshall_with_paths,
    recover_floyd_warshall_path,
)


class FloydWarshallTests(unittest.TestCase):
    def test_finds_all_pairs_paths_with_negative_edge(self):
        distance = floyd_warshall(3, [(0, 1, 4), (0, 2, 11), (1, 2, -2)])
        self.assertEqual(distance[0][2], 2.0)
        self.assertEqual(distance[2][0], inf)
        self.assertEqual([distance[index][index] for index in range(3)], [0.0, 0.0, 0.0])

    def test_uses_best_parallel_edge(self):
        self.assertEqual(floyd_warshall(2, [(0, 1, 8), (0, 1, 3)])[0][1], 3.0)

    def test_recovers_a_shortest_path_and_certifies_next_hops(self):
        edges = [(0, 1, 4), (0, 2, 11), (1, 2, -2)]
        distance, next_hop = floyd_warshall_with_paths(3, edges)
        path = recover_floyd_warshall_path(next_hop, 0, 2)
        self.assertEqual(path, [0, 1, 2])
        self.assertEqual(distance[0][2], 2.0)
        self.assertTrue(floyd_warshall_path_certificate(3, edges, distance, next_hop, 0, 2, path))

    def test_path_recovery_handles_unreachable_and_rejects_tampered_next_hop(self):
        edges = [(0, 1, 4), (1, 2, -2)]
        distance, next_hop = floyd_warshall_with_paths(3, edges)
        self.assertIsNone(recover_floyd_warshall_path(next_hop, 2, 0))
        tampered = [list(row) for row in next_hop]
        tampered[0][2] = 2
        self.assertFalse(floyd_warshall_path_certificate(3, edges, distance, tampered, 0, 2, [0, 2]))

    def test_trace_certificate_replays_each_allowed_intermediate_layer(self):
        edges = [(0, 1, 4), (0, 2, 11), (1, 2, -2)]
        distance, trace = floyd_warshall_trace(3, edges)
        self.assertEqual(distance[0][2], 2.0)
        self.assertTrue(floyd_warshall_trace_certificate(3, edges, distance, trace))
        tampered = list(trace)
        event = tampered[1]
        changed = [list(row) for row in event.distance]
        changed[0][2] = 11.0
        tampered[1] = FloydWarshallEvent(event.middle, tuple(tuple(row) for row in changed))
        self.assertFalse(floyd_warshall_trace_certificate(3, edges, distance, tampered))

    def test_rejects_negative_cycle_and_invalid_inputs(self):
        with self.assertRaises(ValueError):
            floyd_warshall(2, [(0, 1, -1), (1, 0, -1)])
        with self.assertRaises(ValueError):
            floyd_warshall(0, [])
        with self.assertRaises(ValueError):
            floyd_warshall(2, [(0, 2, 1)])
        with self.assertRaises(ValueError):
            floyd_warshall(2, [(0, 1, float("nan"))])


if __name__ == "__main__":
    unittest.main()
