import unittest

from projects.naive_bayes_spam.bootstrap_support import percentile, require_integer


class BootstrapSupportTests(unittest.TestCase):
    def test_shared_integer_contract_and_percentile_convention(self):
        self.assertEqual(require_integer(20, "repeats", 20), 20)
        self.assertEqual(percentile([4.0, 1.0, 3.0, 2.0], .5), 3.0)
        self.assertEqual(percentile([4.0, 1.0, 3.0, 2.0], 0), 1.0)
        self.assertEqual(percentile([4.0, 1.0, 3.0, 2.0], 1), 4.0)

    def test_shared_contract_rejects_invalid_controls(self):
        with self.assertRaisesRegex(ValueError, "repeats"):
            require_integer(True, "repeats", 20)
        with self.assertRaisesRegex(ValueError, "values"):
            percentile([], .5)
        with self.assertRaisesRegex(ValueError, "probability"):
            percentile([1.0], 1.1)


if __name__ == "__main__":
    unittest.main()
