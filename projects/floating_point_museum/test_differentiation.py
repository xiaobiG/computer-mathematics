import math
import unittest

from projects.floating_point_museum.differentiation import central_difference, central_difference_report


class DifferentiationTests(unittest.TestCase):
    def test_sine_step_scan_exposes_second_order_trend_and_roundoff_rebound(self):
        report = central_difference_report(math.sin, math.cos, 1.0)
        self.assertTrue(report["certificate"]["coarse_steps_show_second_order_trend"])
        self.assertTrue(report["certificate"]["small_steps_rebound_after_best"])
        self.assertTrue(report["certificate"]["valid"])
        self.assertLess(report["best"].absolute_error, 1e-10)

    def test_central_difference_handles_a_smooth_function_and_rejects_bad_contracts(self):
        self.assertAlmostEqual(central_difference(math.exp, 0.0, 1e-5), 1.0, places=9)
        with self.assertRaises(ValueError):
            central_difference(math.log, 1e-6, 1e-5)
        with self.assertRaises(ValueError):
            central_difference_report(math.sin, math.cos, 1.0, [1, 2])
        with self.assertRaises(ValueError):
            central_difference(lambda _: float("nan"), 0.0, 1e-3)


if __name__ == "__main__":
    unittest.main()
