import unittest

from projects.crypto_toybox.chinese_remainder import (
    chinese_remainder,
    combine_congruences,
    toy_rsa_crt_fault_certificate,
    toy_rsa_crt_fault_report,
)


class ChineseRemainderTests(unittest.TestCase):
    def test_merges_coprime_congruences_and_recovers_a_hidden_residue(self):
        residue, modulus = chinese_remainder([(2, 3), (3, 5), (2, 7)])
        self.assertEqual((residue, modulus), (23, 105))
        secret = 233
        recovered, total_modulus = chinese_remainder([(secret % 4, 4), (secret % 9, 9), (secret % 5, 5)])
        self.assertEqual(total_modulus, 180)
        self.assertEqual(recovered, secret % total_modulus)

    def test_accepts_compatible_non_coprime_moduli(self):
        residue, modulus = combine_congruences((1, 4), (3, 6))
        self.assertEqual((residue, modulus), (9, 12))
        self.assertEqual(residue % 4, 1)
        self.assertEqual(residue % 6, 3)

    def test_rejects_conflicts_and_invalid_moduli(self):
        with self.assertRaises(ValueError):
            combine_congruences((0, 2), (1, 2))
        with self.assertRaises(ValueError):
            chinese_remainder([])
        with self.assertRaises(ValueError):
            combine_congruences((1, 0), (1, 3))

    def test_toy_rsa_crt_fault_reveals_the_unchanged_branch_factor(self):
        report = toy_rsa_crt_fault_report(5, 11, 3, 7, faulted_branch="p")
        self.assertEqual(report["modulus"], 55)
        self.assertEqual(report["difference_gcd"], 11)
        self.assertEqual(report["cofactor"], 5)
        self.assertTrue(report["nontrivial_factor_recovered"])
        self.assertTrue(report["correct_matches_direct_private_power"])
        self.assertTrue(toy_rsa_crt_fault_certificate(5, 11, 3, 7, "p", report))
        tampered = dict(report)
        tampered["difference_gcd"] = 1
        self.assertFalse(toy_rsa_crt_fault_certificate(5, 11, 3, 7, "p", tampered))

    def test_toy_rsa_crt_fault_contract_is_bounded_and_explicit(self):
        with self.assertRaises(ValueError):
            toy_rsa_crt_fault_report(5, 11, 3, 7, faulted_branch="unknown")
        with self.assertRaises(ValueError):
            toy_rsa_crt_fault_report(1_009, 11, 3, 7, faulted_branch="p")


if __name__ == "__main__":
    unittest.main()
