import unittest

from projects.naive_bayes_spam.cost_sensitive_decisions import (
    cost_sensitive_decision,
    cost_sensitive_decision_table,
)


class CostSensitiveDecisionTests(unittest.TestCase):
    def test_same_probability_changes_action_when_declared_costs_change(self):
        balanced = cost_sensitive_decision(0.2, false_positive_cost=1.0, false_negative_cost=1.0)
        missed_spam_is_costly = cost_sensitive_decision(0.2, false_positive_cost=1.0, false_negative_cost=9.0)

        self.assertEqual(balanced.positive_threshold, 0.5)
        self.assertFalse(balanced.recommended_label)
        self.assertEqual(missed_spam_is_costly.positive_threshold, 0.1)
        self.assertTrue(missed_spam_is_costly.recommended_label)

    def test_table_preserves_each_forecast_and_an_exact_tie_requires_policy(self):
        decisions = cost_sensitive_decision_table([0.1, 0.5, 0.9], 1.0, 1.0)
        self.assertEqual([decision.probability for decision in decisions], [0.1, 0.5, 0.9])
        self.assertEqual([decision.recommended_label for decision in decisions], [False, None, True])

    def test_rejects_invalid_probabilities_costs_and_empty_tables(self):
        with self.assertRaises(ValueError):
            cost_sensitive_decision(1.1, 1.0, 1.0)
        with self.assertRaises(ValueError):
            cost_sensitive_decision(0.3, 0.0, 1.0)
        with self.assertRaises(ValueError):
            cost_sensitive_decision_table([], 1.0, 1.0)


if __name__ == "__main__":
    unittest.main()
