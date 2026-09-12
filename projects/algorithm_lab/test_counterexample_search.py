import unittest

from projects.algorithm_lab.counterexample_search import (
    bounded_binary_search_counterexample,
    bounded_binary_search_counterexample_certificate,
)


class CounterexampleSearchTests(unittest.TestCase):
    def test_nonprogress_update_has_a_finite_stalling_witness(self):
        report = bounded_binary_search_counterexample("nonprogress_left", max_length=2, max_value=2)
        self.assertEqual(report["failure"], "interval_did_not_strictly_shrink")
        self.assertTrue(bounded_binary_search_counterexample_certificate(
            "nonprogress_left", max_length=2, max_value=2, report=report,
        ))

    def test_wrong_right_update_loses_a_present_target(self):
        report = bounded_binary_search_counterexample("drops_left_boundary", max_length=2, max_value=2)
        self.assertEqual(report["failure"], "present_target_lost")
        self.assertIn(report["target"], report["values"])
        self.assertTrue(bounded_binary_search_counterexample_certificate(
            "drops_left_boundary", max_length=2, max_value=2, report=report,
        ))

    def test_certificate_binds_fault_domain_and_witness(self):
        report = bounded_binary_search_counterexample("nonprogress_left", max_length=2, max_value=2)
        report["failure"] = "present_target_lost"
        self.assertFalse(bounded_binary_search_counterexample_certificate(
            "nonprogress_left", max_length=2, max_value=2, report=report,
        ))
        with self.assertRaises(ValueError):
            bounded_binary_search_counterexample("wrong-update")


if __name__ == "__main__":
    unittest.main()
