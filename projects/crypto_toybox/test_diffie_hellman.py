import unittest

from projects.crypto_toybox.diffie_hellman import (
    HonestExchange,
    MitmExchange,
    dh_shared,
    generator_order,
    honest_exchange,
    honest_exchange_certificate,
    mitm_exchange,
    mitm_exchange_certificate,
)


class DiffieHellmanTests(unittest.TestCase):
    def test_honest_tiny_exchange_has_one_shared_element(self):
        exchange = honest_exchange(5, 23, 6, 15)
        self.assertEqual(generator_order(5, 23), 22)
        self.assertEqual(exchange.alice_shared, exchange.bob_shared)
        self.assertTrue(honest_exchange_certificate(5, 23, 6, 15, exchange)["valid"])

    def test_man_in_the_middle_gets_two_matching_but_distinct_sessions(self):
        exchange = mitm_exchange(5, 23, 6, 15, 7, 8)
        self.assertEqual(exchange.alice_shared_with_mallory, exchange.mallory_with_alice)
        self.assertEqual(exchange.bob_shared_with_mallory, exchange.mallory_with_bob)
        self.assertNotEqual(exchange.alice_shared_with_mallory, exchange.bob_shared_with_mallory)
        self.assertTrue(mitm_exchange_certificate(5, 23, 6, 15, 7, 8, exchange)["valid"])

    def test_exchange_certificates_reject_tampered_public_or_session_values(self):
        honest = honest_exchange(5, 23, 6, 15)
        tampered_honest = HonestExchange(
            honest.alice_public + 1, honest.bob_public, honest.alice_shared, honest.bob_shared,
        )
        self.assertFalse(honest_exchange_certificate(5, 23, 6, 15, tampered_honest)["valid"])

        intercepted = mitm_exchange(5, 23, 6, 15, 7, 8)
        tampered_mitm = MitmExchange(
            intercepted.alice_shared_with_mallory, intercepted.bob_shared_with_mallory,
            intercepted.mallory_with_alice, (intercepted.mallory_with_bob + 1) % 23,
        )
        certificate = mitm_exchange_certificate(5, 23, 6, 15, 7, 8, tampered_mitm)
        self.assertFalse(certificate["bob_session_matches_mallory"])
        self.assertFalse(certificate["valid"])

    def test_rejects_trivial_or_out_of_contract_values(self):
        with self.assertRaises(ValueError):
            dh_shared(1, 6, 23)
        with self.assertRaises(ValueError):
            honest_exchange(5, 21, 6, 15)
        with self.assertRaises(ValueError):
            honest_exchange(5, 23, 0, 15)
