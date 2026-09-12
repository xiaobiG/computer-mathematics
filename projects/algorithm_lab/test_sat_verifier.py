import unittest

from projects.algorithm_lab.sat_verifier import (
    find_satisfying_assignment,
    independent_set_cnf_certificate,
    independent_set_cnf_report,
    independent_set_to_cnf,
    verify_assignment,
    variables,
)


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

    def test_independent_set_reduction_matches_a_small_exhaustive_oracle(self):
        vertices = ["a", "b", "c", "d"]
        path_edges = [("a", "b"), ("b", "c"), ("c", "d")]
        report = independent_set_cnf_report(vertices, path_edges, 2)
        self.assertTrue(report["cnf_satisfiable"])
        self.assertTrue(report["small_instance_independent_set_oracle"])
        self.assertTrue(report["yes_no_agree"])
        self.assertEqual(len(report["decoded_independent_set"]), 2)
        self.assertTrue(independent_set_cnf_certificate(vertices, path_edges, 2, report))

        triangle = [("a", "b"), ("b", "c"), ("a", "c")]
        impossible = independent_set_cnf_report(["a", "b", "c"], triangle, 2)
        self.assertFalse(impossible["cnf_satisfiable"])
        self.assertFalse(impossible["small_instance_independent_set_oracle"])

    def test_reduction_rejects_changed_formula_and_invalid_graph_contracts(self):
        vertices, edges = ["a", "b", "c"], [("a", "b")]
        report = independent_set_cnf_report(vertices, edges, 2)
        changed = dict(report)
        changed["clause_count"] = report["clause_count"] + 1
        self.assertFalse(independent_set_cnf_certificate(vertices, edges, 2, changed))
        with self.assertRaises(ValueError):
            independent_set_to_cnf(["a", "a"], [], 1)
        with self.assertRaises(ValueError):
            independent_set_to_cnf(["a", "b"], [("a", "a")], 1)


if __name__ == "__main__":
    unittest.main()
