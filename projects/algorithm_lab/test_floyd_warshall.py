import unittest
from math import inf

from projects.algorithm_lab.floyd_warshall import floyd_warshall


class FloydWarshallTests(unittest.TestCase):
    def test_finds_all_pairs_paths_with_negative_edge(self):
        distance = floyd_warshall(3, [(0, 1, 4), (0, 2, 11), (1, 2, -2)])
        self.assertEqual(distance[0][2], 2.0)
        self.assertEqual(distance[2][0], inf)
        self.assertEqual([distance[index][index] for index in range(3)], [0.0, 0.0, 0.0])

    def test_uses_best_parallel_edge(self):
        self.assertEqual(floyd_warshall(2, [(0, 1, 8), (0, 1, 3)])[0][1], 3.0)

    def test_rejects_negative_cycle_and_invalid_inputs(self):
        with self.assertRaises(ValueError):
            floyd_warshall(2, [(0, 1, -1), (1, 0, -1)])
        with self.assertRaises(ValueError):
            floyd_warshall(0, [])
        with self.assertRaises(ValueError):
            floyd_warshall(2, [(0, 2, 1)])


if __name__ == "__main__":
    unittest.main()
