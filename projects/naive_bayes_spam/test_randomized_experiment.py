import copy
import unittest

from projects.naive_bayes_spam.randomized_experiment import (
    assignment_mean_difference,
    complete_randomization_certificate,
    complete_randomization_report,
)


class RandomizedExperimentTests(unittest.TestCase):
    def setUp(self):
        # Each pair is (outcome under control, outcome under treatment).
        self.outcomes = [(0.0, 1.0), (0.0, 2.0), (1.0, 1.0), (1.0, 3.0)]

    def test_complete_randomization_expectation_matches_finite_population_effect(self):
        report = complete_randomization_report(self.outcomes, treated_count=2)
        self.assertEqual(report["assignment_count"], 6)
        self.assertAlmostEqual(report["finite_population_average_treatment_effect"], 1.25)
        self.assertAlmostEqual(report["expected_difference_in_means"], 1.25)
        self.assertAlmostEqual(report["expectation_minus_effect"], 0.0)
        self.assertTrue(complete_randomization_certificate(self.outcomes, 2, report))

    def test_one_assignment_can_differ_from_its_randomization_expectation(self):
        report = complete_randomization_report(self.outcomes, treated_count=2)
        self.assertAlmostEqual(assignment_mean_difference(self.outcomes, [0, 1]), 0.5)
        self.assertLess(assignment_mean_difference(self.outcomes, [0, 1]), report["expected_difference_in_means"])
        altered = copy.deepcopy(report)
        altered["assignment_mechanism"] = "observational_assignment"
        self.assertFalse(complete_randomization_certificate(self.outcomes, 2, altered))

    def test_contract_rejects_invalid_assignments_and_unusable_tables(self):
        with self.assertRaises(ValueError):
            complete_randomization_report([(0.0, 1.0)], 1)
        with self.assertRaises(ValueError):
            complete_randomization_report(self.outcomes, 0)
        with self.assertRaises(ValueError):
            assignment_mean_difference(self.outcomes, [0, 0])


if __name__ == "__main__":
    unittest.main()
