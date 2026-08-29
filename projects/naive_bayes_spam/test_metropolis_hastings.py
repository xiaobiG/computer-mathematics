import unittest

from projects.naive_bayes_spam.metropolis_hastings import (
    McmcEvent, empirical_probabilities, metropolis_hastings, metropolis_hastings_trace_certificate,
)


TARGET = {0: 1.0, 1: 3.0}
SYMMETRIC_PROPOSAL = {0: {1: 1.0}, 1: {0: 1.0}}


class MetropolisHastingsTests(unittest.TestCase):
    def test_acceptance_corrects_a_symmetric_proposal_toward_target_weights(self):
        samples, trace = metropolis_hastings(TARGET, SYMMETRIC_PROPOSAL, 0, steps=10_000, seed=2026)
        frequencies = empirical_probabilities(samples[500:])
        self.assertAlmostEqual(frequencies[1], 0.75, delta=0.04)
        self.assertEqual(trace[0].acceptance_probability, 1.0)
        self.assertAlmostEqual(trace[1].acceptance_probability, 1 / 3)

    def test_asymmetric_proposal_uses_reverse_transition_probability(self):
        proposal = {0: {1: 1.0}, 1: {0: 0.25, 1: 0.75}}
        _, trace = metropolis_hastings({0: 1.0, 1: 1.0}, proposal, 0, steps=2, seed=4)
        self.assertEqual(trace[0].acceptance_probability, 0.25)

    def test_trace_certificate_replays_seeded_proposals_and_acceptance_draws(self):
        samples, trace = metropolis_hastings(TARGET, SYMMETRIC_PROPOSAL, 0, steps=12, seed=17)
        self.assertTrue(metropolis_hastings_trace_certificate(
            TARGET, SYMMETRIC_PROPOSAL, 0, samples, trace, seed=17,
        ))
        tampered = list(trace)
        event = tampered[3]
        tampered[3] = McmcEvent(
            event.previous, event.proposed, event.current, event.accepted,
            event.acceptance_probability / 2.0,
        )
        self.assertFalse(metropolis_hastings_trace_certificate(
            TARGET, SYMMETRIC_PROPOSAL, 0, samples, tampered, seed=17,
        ))

    def test_rejects_invalid_chain_contracts(self):
        with self.assertRaises(ValueError):
            metropolis_hastings(TARGET, {0: {1: 1.0}, 1: {0: 0.9}}, 0, steps=2)
        with self.assertRaises(ValueError):
            metropolis_hastings(TARGET, SYMMETRIC_PROPOSAL, 2, steps=2)
        with self.assertRaises(ValueError):
            empirical_probabilities([])
