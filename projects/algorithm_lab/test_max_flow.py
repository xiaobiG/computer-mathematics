import unittest

from projects.algorithm_lab.max_flow import max_flow


EDGES = [
    (0, 1, 3.0), (0, 2, 2.0), (1, 2, 1.0), (1, 3, 2.0),
    (2, 3, 3.0),
]


class MaxFlowTests(unittest.TestCase):
    def test_augmenting_paths_reach_value_and_min_cut_certificate(self):
        value, source_side, trace = max_flow(4, EDGES, 0, 3)
        cut_capacity = sum(capacity for left, right, capacity in EDGES if left in source_side and right not in source_side)
        self.assertEqual(value, 5.0)
        self.assertEqual(cut_capacity, value)
        self.assertEqual(trace[-1].total_flow, value)
        self.assertTrue(all(event.path[0] == 0 and event.path[-1] == 3 for event in trace))

    def test_parallel_edges_and_no_path_are_handled(self):
        self.assertEqual(max_flow(2, [(0, 1, 1.0), (0, 1, 2.0)], 0, 1)[0], 3.0)
        value, source_side, trace = max_flow(3, [(0, 1, 1.0)], 0, 2)
        self.assertEqual((value, source_side, trace), (0.0, {0, 1}, []))

    def test_rejects_invalid_flow_contracts(self):
        with self.assertRaises(ValueError):
            max_flow(1, [], 0, 0)
        with self.assertRaises(ValueError):
            max_flow(2, [(0, 1, -1.0)], 0, 1)
        with self.assertRaises(ValueError):
            max_flow(2, [(0, 2, 1.0)], 0, 1)
