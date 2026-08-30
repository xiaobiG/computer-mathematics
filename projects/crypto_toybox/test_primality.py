import unittest

from projects.crypto_toybox.primality import (
    MillerRabinRound,
    decompose_power_of_two,
    miller_rabin_report,
    miller_rabin_report_certificate,
    miller_rabin_round,
    miller_rabin_round_certificate,
)


class PrimalityTests(unittest.TestCase):
    def test_miller_rabin_round_records_a_replayable_composite_witness(self):
        event = miller_rabin_round(561, 2)
        self.assertEqual((event.twos, event.odd_part), (4, 35))
        self.assertFalse(event.passes)
        self.assertTrue(miller_rabin_round_certificate(561, event))
        tampered_chain = ((event.square_chain[0] + 1) % 561,) + event.square_chain[1:]
        tampered = MillerRabinRound(event.base, event.twos, event.odd_part, tampered_chain, event.passes)
        self.assertFalse(miller_rabin_round_certificate(561, tampered))

    def test_report_distinguishes_a_witness_from_probable_prime_rounds(self):
        composite = miller_rabin_report(561, [2, 3, 5])
        self.assertFalse(composite["probably_prime"])
        self.assertTrue(composite["witnesses"])
        self.assertTrue(composite["certificate"]["all_rounds_replay"])
        self.assertTrue(miller_rabin_report_certificate(561, [2, 3, 5], composite)["valid"])

        tampered = dict(composite)
        tampered["probably_prime"] = True
        certificate = miller_rabin_report_certificate(561, [2, 3, 5], tampered)
        self.assertFalse(certificate["fields_match_recomputed_report"])
        self.assertFalse(certificate["valid"])

        prime = miller_rabin_report(1_000_000_007, [2, 3, 5])
        self.assertTrue(prime["probably_prime"])
        self.assertEqual(prime["witnesses"], [])
        self.assertTrue(prime["certificate"]["valid"])
        self.assertTrue(miller_rabin_report_certificate(1_000_000_007, [2, 3, 5], prime)["valid"])

    def test_contracts_reject_invalid_candidates_and_bases(self):
        self.assertEqual(decompose_power_of_two(560), (4, 35))
        with self.assertRaises(ValueError):
            miller_rabin_round(4, 2)
        with self.assertRaises(ValueError):
            miller_rabin_round(561, 1)
        with self.assertRaises(ValueError):
            miller_rabin_report(561, [])
