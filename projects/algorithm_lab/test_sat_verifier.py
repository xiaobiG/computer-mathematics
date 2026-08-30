import unittest

from projects.algorithm_lab.sat_verifier import find_satisfying_assignment, verify_assignment, variables


class SatVerifierTests(unittest.TestCase):
    def test_verifier_accepts_a_witness(self):
        formula = ((1, -2), (2, 3), (-1, 3))
        self.assertTrue(verify_assignment(formula, {1: True, 2: True, 3: True}))

    def test_verifier_rejects_an_invalid_witness(self):
        formula = ((1,), (-2,))
        self.assertFalse(verify_assignment(formula, {1: False, 2: True}))

    def test_brute_force_finds_witness_or_proves_exhaustion(self):
        satisfiable = ((1, 2), (-1, 2))
        witness = find_satisfying_assignment(satisfiable)
        self.assertIsNotNone(witness)
        self.assertTrue(verify_assignment(satisfiable, witness))
        self.assertIsNone(find_satisfying_assignment(((1,), (-1,))))

    def test_exhaustive_search_has_an_explicit_variable_budget(self):
        formula = ((1,), (2,), (3,))
        self.assertTrue(verify_assignment(formula, find_satisfying_assignment(formula, max_variables=3)))
        with self.assertRaises(ValueError):
            find_satisfying_assignment(formula, max_variables=2)
        with self.assertRaises(ValueError):
            find_satisfying_assignment(formula, max_variables=-1)

    def test_rejects_missing_extra_or_malformed_variables(self):
        with self.assertRaises(ValueError):
            verify_assignment(((1,),), {})
        with self.assertRaises(ValueError):
            verify_assignment(((1,),), {1: True, 2: False})
        with self.assertRaises(ValueError):
            variables(((0,),))
        with self.assertRaises(ValueError):
            variables(((),))


if __name__ == "__main__":
    unittest.main()
