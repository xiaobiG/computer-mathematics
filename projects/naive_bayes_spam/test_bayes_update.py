import unittest

from projects.naive_bayes_spam.bayes_update import posterior, posterior_trace


class BayesUpdateTests(unittest.TestCase):
    def test_low_base_rate_example_keeps_the_normalising_evidence(self):
        update = posterior(0.01, 0.90, 0.05)
        self.assertAlmostEqual(update.evidence, 0.0585)
        self.assertAlmostEqual(update.posterior, 0.009 / 0.0585)
        self.assertLess(update.posterior, 0.2)

    def test_two_independent_supporting_observations_update_sequentially(self):
        final, trace = posterior_trace(0.1, [(0.8, 0.2), (0.8, 0.2)])
        self.assertEqual(len(trace), 2)
        self.assertGreater(trace[0].posterior, trace[0].prior)
        self.assertGreater(final, trace[0].posterior)
        self.assertAlmostEqual(trace[1].prior, trace[0].posterior)

    def test_uninformative_evidence_leaves_the_prior_unchanged(self):
        update = posterior(0.37, 0.4, 0.4)
        self.assertAlmostEqual(update.posterior, 0.37)

    def test_rejects_invalid_and_impossible_evidence(self):
        with self.assertRaises(ValueError):
            posterior(1.1, 0.5, 0.5)
        with self.assertRaises(ValueError):
            posterior(0.5, 0.0, 0.0)
