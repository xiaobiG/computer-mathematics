import unittest

from projects.floating_point_museum.examples import (
    kahan_sum,
    nearly_equal,
    naive_sum,
    naive_root_difference,
    stable_root_difference,
)


class FloatingPointMuseumTests(unittest.TestCase):
    def test_nearly_equal_handles_decimal_representation(self):
        self.assertTrue(nearly_equal(0.1 + 0.2, 0.3))

    def test_kahan_recovers_small_terms(self):
        self.assertEqual(naive_sum([1e16, 1.0, 1.0, -1e16]), 0.0)
        self.assertEqual(kahan_sum([1e16, 1.0, 1.0, -1e16]), 2.0)

    def test_stable_root_difference_avoids_cancellation(self):
        self.assertEqual(naive_root_difference(1e16), 0.0)
        self.assertGreater(stable_root_difference(1e16), 0.0)


if __name__ == "__main__":
    unittest.main()
