import unittest

from projects.crypto_toybox.finite_group import (
    discrete_log_toy,
    finite_group_certificate,
    finite_group_report,
    multiplicative_order,
    primitive_generators,
    subgroup_elements,
)


class FiniteGroupTests(unittest.TestCase):
    def test_orders_and_generators_enumerate_the_expected_small_groups(self):
        self.assertEqual(multiplicative_order(2, 23), 11)
        self.assertEqual(len(subgroup_elements(2, 23)), 11)
        self.assertEqual(multiplicative_order(5, 23), 22)
        self.assertIn(5, primitive_generators(23))
        self.assertEqual(set(subgroup_elements(5, 23)), set(range(1, 23)))

    def test_toy_discrete_log_recovers_only_a_small_group_exponent(self):
        self.assertEqual(discrete_log_toy(5, pow(5, 7, 23), 23), 7)
        self.assertIsNone(discrete_log_toy(2, 5, 23))

    def test_rejects_composite_moduli_zero_and_large_enumeration(self):
        with self.assertRaises(ValueError):
            multiplicative_order(2, 15)
        with self.assertRaises(ValueError):
            multiplicative_order(0, 23)
        with self.assertRaises(ValueError):
            discrete_log_toy(2, 3, 1_009)

    def test_group_report_certifies_subgroup_closure_inverses_and_generator_scope(self):
        subgroup = finite_group_report(2, 23)
        self.assertEqual(subgroup["order"], 11)
        self.assertFalse(subgroup["generator_spans_full_group"])
        self.assertTrue(finite_group_certificate(2, 23, subgroup)["valid"])

        full_group = finite_group_report(5, 23)
        self.assertTrue(full_group["generator_spans_full_group"])
        self.assertTrue(finite_group_certificate(5, 23, full_group)["valid"])

        tampered = dict(subgroup)
        tampered["elements"] = subgroup["elements"][:-1] + (5,)
        certificate = finite_group_certificate(2, 23, tampered)
        self.assertFalse(certificate["fields_match_recomputed_group"])
        self.assertFalse(certificate["valid"])
