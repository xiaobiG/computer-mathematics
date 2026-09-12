import unittest

from projects.floating_point_museum.examples import (
    kahan_sum,
    kahan_sum_trace,
    kahan_sum_trace_certificate,
    nearly_equal,
    naive_sum,
    pairwise_sum,
    naive_root_difference,
    stable_root_difference,
)


class FloatingPointMuseumTests(unittest.TestCase):
    def test_nearly_equal_handles_decimal_representation(self):
        self.assertTrue(nearly_equal(0.1 + 0.2, 0.3))

    def test_kahan_recovers_small_terms(self):
        self.assertEqual(naive_sum([1e16, 1.0, 1.0, -1e16]), 0.0)
        self.assertEqual(kahan_sum([1e16, 1.0, 1.0, -1e16]), 2.0)

    def test_kahan_trace_replays_compensation_state(self):
        values = [1e16, 1.0, 1.0, -1e16]
        result, events = kahan_sum_trace(values)
        self.assertEqual(result, 2.0)
        self.assertEqual([event.corrected for event in events], [1e16, 1.0, 2.0, -1e16])
        self.assertEqual([event.compensation_after for event in events], [0.0, -1.0, 0.0, 0.0])
        self.assertTrue(kahan_sum_trace_certificate(values, result, events))
        tampered = list(events)
        event = tampered[1]
        tampered[1] = event.__class__(
            event.iteration, event.value, event.total_before, event.compensation_before,
            event.corrected, event.total_after, 0.0,
        )
        self.assertFalse(kahan_sum_trace_certificate(values, result, tampered))

    def test_pairwise_handles_empty_odd_and_fixed_tree_order(self):
        self.assertEqual(pairwise_sum([]), 0.0)
        self.assertEqual(pairwise_sum([1.0, 2.0, 3.0]), 6.0)
        self.assertEqual(pairwise_sum([1e16, 1.0, 1.0, -1e16]), 0.0)
        self.assertEqual(pairwise_sum([1e16, -1e16, 1.0, 1.0]), 2.0)

    def test_stable_root_difference_avoids_cancellation(self):
        self.assertEqual(naive_root_difference(1e16), 0.0)
        self.assertGreater(stable_root_difference(1e16), 0.0)


if __name__ == "__main__":
    unittest.main()
