import copy
import unittest

from projects.naive_bayes_spam.randomized_experiment import (
    assignment_mean_difference,
    complete_randomization_certificate,
    complete_randomization_report,
    two_unit_interference_certificate,
    two_unit_interference_report,
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

    def test_interference_breaks_the_complete_randomization_direct_effect_identity(self):
        # Y_i(z_i, z_peer) = 2*z_i + 3*z_peer for both units.
        outcomes = [(0.0, 3.0, 2.0, 5.0), (0.0, 3.0, 2.0, 5.0)]
        report = two_unit_interference_report(outcomes)
        self.assertFalse(report["no_interference_condition_holds"])
        self.assertEqual(report["average_direct_effect_when_peer_control"], 2.0)
        self.assertEqual(report["expected_treated_minus_control"], -1.0)
        self.assertEqual(report["expectation_minus_direct_effect"], -3.0)
        self.assertTrue(two_unit_interference_certificate(outcomes, report))

    def test_interference_certificate_rejects_tampering_and_contract_rejects_wrong_shape(self):
        outcomes = [(0.0, 3.0, 2.0, 5.0), (0.0, 3.0, 2.0, 5.0)]
        report = two_unit_interference_report(outcomes)
        report["expected_treated_minus_control"] = 2.0
        self.assertFalse(two_unit_interference_certificate(outcomes, report))
        with self.assertRaises(ValueError):
            two_unit_interference_report([(0.0, 1.0, 2.0, 3.0)])


if __name__ == "__main__":
    unittest.main()
