import copy
import unittest

from projects.naive_bayes_spam.block_window_calibration_bootstrap import block_window_calibration_bootstrap_certificate, block_window_calibration_bootstrap_report
from projects.naive_bayes_spam.labeled_window_monitoring import LABELED_WINDOW_CONTRACT_VERSION


def block(probabilities, labels):
    return {"contract_version": LABELED_WINDOW_CONTRACT_VERSION, "probabilities": probabilities, "labels": labels}


class BlockWindowCalibrationBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.reference = [block([.5, .5], [1, 0]), block([.5, .5], [1, 0])]
        self.current = [block([.8, .8], [1, 0]), block([.8, .8], [1, 0])]

    def test_fixed_seed_block_report_replays_and_preserves_block_policy(self):
        report = block_window_calibration_bootstrap_report("old", self.reference, "new", self.current, minimum_window_size=4, repeats=20, seed=7)
        self.assertEqual(report["bootstrap_policy"]["resampling_unit"], "predefined_labeled_time_block")
        self.assertEqual(report["block_sizes"], {"reference": [2, 2], "current": [2, 2]})
        self.assertEqual(report["minimum_possible_resample_sizes"], {"reference": 4, "current": 4})
        self.assertTrue(block_window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, report))

    def test_certificate_and_policy_reject_tampering_or_one_block_input(self):
        report = block_window_calibration_bootstrap_report("old", self.reference, "new", self.current, minimum_window_size=4, repeats=20, seed=7)
        tampered = copy.deepcopy(report)
        tampered["block_sizes"]["current"] = [4]
        self.assertFalse(block_window_calibration_bootstrap_certificate("old", self.reference, "new", self.current, tampered))
        with self.assertRaisesRegex(ValueError, "at least two"):
            block_window_calibration_bootstrap_report("old", self.reference[:1], "new", self.current, minimum_window_size=2, repeats=20)

    def test_rejects_unequal_blocks_when_a_complete_block_resample_can_be_too_small(self):
        sparse_blocks = [block([.5] * 19, [1] * 19), block([.5], [0])]
        with self.assertRaisesRegex(ValueError, "can produce.*only 2"):
            block_window_calibration_bootstrap_report(
                "old", sparse_blocks, "new", sparse_blocks, minimum_window_size=20, repeats=20,
            )


if __name__ == "__main__":
    unittest.main()
