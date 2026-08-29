import unittest

from projects.algorithm_lab.weighted_activity import (
    brute_force_best_value,
    compatible_schedule,
    weighted_activity_selection,
)


class WeightedActivityTests(unittest.TestCase):
    def test_dp_beats_the_earliest_finish_counterexample(self):
        activities = [(0.0, 2.0, 1.0, "short"), (0.0, 4.0, 100.0, "valuable")]
        value, chosen = weighted_activity_selection(activities)
        self.assertEqual(value, 100.0)
        self.assertEqual([activity[3] for activity in chosen], ["valuable"])

    def test_reconstruction_is_compatible_and_matches_brute_force_oracle(self):
        activities = [
            (0.0, 3.0, 5.0, "a"), (1.0, 4.0, 6.0, "b"), (3.0, 5.0, 5.0, "c"),
            (0.0, 6.0, 11.0, "d"), (5.0, 7.0, 4.0, "e"),
        ]
        value, chosen = weighted_activity_selection(activities)
        self.assertTrue(compatible_schedule(chosen))
        self.assertEqual(sum(activity[2] for activity in chosen), value)
        self.assertEqual(value, brute_force_best_value(activities))

    def test_rejects_invalid_activities_and_large_brute_force_requests(self):
        with self.assertRaises(ValueError):
            weighted_activity_selection([(2.0, 1.0, 1.0, "bad")])
        with self.assertRaises(ValueError):
            weighted_activity_selection([(0.0, 1.0, -1.0, "bad")])
        with self.assertRaises(ValueError):
            brute_force_best_value([(float(index), float(index + 1), 1.0, str(index)) for index in range(19)])
