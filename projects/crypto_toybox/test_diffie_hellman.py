import unittest

from projects.crypto_toybox.diffie_hellman import dh_shared, generator_order, honest_exchange, mitm_exchange


class DiffieHellmanTests(unittest.TestCase):
    def test_honest_tiny_exchange_has_one_shared_element(self):
        exchange = honest_exchange(5, 23, 6, 15)
        self.assertEqual(generator_order(5, 23), 22)
        self.assertEqual(exchange.alice_shared, exchange.bob_shared)

    def test_man_in_the_middle_gets_two_matching_but_distinct_sessions(self):
        exchange = mitm_exchange(5, 23, 6, 15, 7, 8)
        self.assertEqual(exchange.alice_shared_with_mallory, exchange.mallory_with_alice)
        self.assertEqual(exchange.bob_shared_with_mallory, exchange.mallory_with_bob)
        self.assertNotEqual(exchange.alice_shared_with_mallory, exchange.bob_shared_with_mallory)

    def test_rejects_trivial_or_out_of_contract_values(self):
        with self.assertRaises(ValueError):
            dh_shared(1, 6, 23)
        with self.assertRaises(ValueError):
            honest_exchange(5, 21, 6, 15)
        with self.assertRaises(ValueError):
            honest_exchange(5, 23, 0, 15)
