import itertools
import unittest

from projects.algorithm_lab.binary_search_trace import (
    binary_search_trace,
    lower_bound_trace,
    lower_bound_trace_respects_invariant,
    trace_respects_invariant,
)


class BinarySearchTraceTests(unittest.TestCase):
    def test_trace_records_half_open_interval_progress(self):
        result, steps = binary_search_trace([1, 3, 5, 7], 7)
        self.assertEqual(result, 3)
        self.assertEqual(steps[0].relation, "less")
        self.assertTrue(trace_respects_invariant([1, 3, 5, 7], 7, result, steps))

    def test_absent_target_ends_with_an_empty_interval(self):
        result, steps = binary_search_trace([1, 3, 5, 7], 4)
        self.assertEqual(result, -1)
        self.assertTrue(trace_respects_invariant([1, 3, 5, 7], 4, result, steps))
        self.assertTrue(steps[-1].next_left == steps[-1].next_right)

    def test_property_on_small_sorted_inputs_including_duplicates(self):
        for length in range(5):
            for values in itertools.combinations_with_replacement(range(4), length):
                for target in range(-1, 5):
                    result, steps = binary_search_trace(list(values), target)
                    self.assertTrue(trace_respects_invariant(list(values), target, result, steps))
                    self.assertEqual(result == -1, target not in values)
                    if result != -1:
                        self.assertEqual(values[result], target)

    def test_unsorted_input_is_rejected_instead_of_silently_losing_the_proof(self):
        with self.assertRaises(ValueError):
            binary_search_trace([2, 1, 3], 1)

    def test_lower_bound_returns_the_boundary_of_a_duplicate_block(self):
        result, steps = lower_bound_trace([1, 3, 3, 3, 7], 3)
        self.assertEqual(result, 1)
        self.assertTrue(lower_bound_trace_respects_invariant([1, 3, 3, 3, 7], 3, result, steps))

    def test_lower_bound_handles_both_end_insertion_points(self):
        for target, expected in [(0, 0), (8, 4)]:
            result, steps = lower_bound_trace([1, 3, 5, 7], target)
            self.assertEqual(result, expected)
            self.assertTrue(lower_bound_trace_respects_invariant([1, 3, 5, 7], target, result, steps))

    def test_lower_bound_property_on_small_sorted_inputs(self):
        for length in range(5):
            for values in itertools.combinations_with_replacement(range(4), length):
                for target in range(-1, 5):
                    result, steps = lower_bound_trace(list(values), target)
                    self.assertTrue(lower_bound_trace_respects_invariant(list(values), target, result, steps))
