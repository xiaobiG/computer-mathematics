import unittest

from projects.crypto_toybox.main import (
    decrypt,
    encrypt,
    mod_pow,
    modular_inverse,
    toy_rsa_keypair,
)


class CryptoToyboxTests(unittest.TestCase):
    def test_fast_power_matches_known_result(self):
        self.assertEqual(mod_pow(7, 128, 13), pow(7, 128, 13))

    def test_modular_inverse(self):
        inverse = modular_inverse(17, 3120)
        self.assertEqual((17 * inverse) % 3120, 1)

    def test_toy_rsa_round_trip(self):
        key = toy_rsa_keypair(61, 53, 17)
        self.assertEqual(key.private_exponent, 2753)
        self.assertEqual(decrypt(encrypt(65, key), key), 65)

    def test_invalid_message_is_rejected(self):
        key = toy_rsa_keypair(61, 53, 17)
        with self.assertRaises(ValueError):
            encrypt(key.modulus, key)


if __name__ == "__main__":
    unittest.main()
