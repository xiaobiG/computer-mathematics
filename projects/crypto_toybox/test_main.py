import unittest

from projects.crypto_toybox.main import (
    decrypt,
    encrypt,
    mod_pow,
    mod_pow_trace,
    mod_pow_trace_certificate,
    modular_inverse,
    raw_rsa_properties,
    RsaKeyPair,
    rsa_keypair_certificate,
    rsa_round_trip_report,
    toy_rsa_keypair,
)


class CryptoToyboxTests(unittest.TestCase):
    def test_fast_power_matches_known_result(self):
        self.assertEqual(mod_pow(7, 128, 13), pow(7, 128, 13))

    def test_fast_power_trace_certifies_each_bit_update_and_rejects_tampering(self):
        result, events = mod_pow_trace(3, 13, 7)
        self.assertEqual(result, pow(3, 13, 7))
        self.assertEqual([event.bit for event in events], [1, 0, 1, 1])
        self.assertTrue(mod_pow_trace_certificate(3, 13, 7, result, events))
        tampered = list(events)
        tampered[1] = tampered[1].__class__(
            tampered[1].iteration, tampered[1].exponent_before, tampered[1].bit,
            (tampered[1].result_after + 1) % 7, tampered[1].base_after, tampered[1].exponent_after,
        )
        self.assertFalse(mod_pow_trace_certificate(3, 13, 7, result, tampered))

    def test_modular_inverse(self):
        inverse = modular_inverse(17, 3120)
        self.assertEqual((17 * inverse) % 3120, 1)

    def test_toy_rsa_round_trip(self):
        key = toy_rsa_keypair(61, 53, 17)
        self.assertEqual(key.private_exponent, 2753)
        self.assertEqual(decrypt(encrypt(65, key), key), 65)

    def test_keypair_certificate_audits_theorem_preconditions_and_rejects_tampering(self):
        key = toy_rsa_keypair(5, 11, 3)
        self.assertEqual(
            rsa_keypair_certificate(5, 11, key),
            {
                "distinct_prime_factors": True,
                "modulus_matches_factors": True,
                "public_exponent_is_a_unit": True,
                "private_exponent_is_inverse": True,
                "valid": True,
            },
        )
        tampered = RsaKeyPair(key.modulus, key.public_exponent, key.private_exponent + 1)
        self.assertFalse(rsa_keypair_certificate(5, 11, tampered)["private_exponent_is_inverse"])
        self.assertFalse(rsa_keypair_certificate(5, 11, tampered)["valid"])

    def test_round_trip_report_covers_coprime_and_non_coprime_messages(self):
        key = toy_rsa_keypair(5, 11, 3)
        report = rsa_round_trip_report([0, 5, 7, 11, 50], key)
        self.assertTrue(report["all_recovered"])
        self.assertEqual(report["non_coprime_messages"], [0, 5, 11, 50])
        self.assertEqual([recovered for _, _, recovered in report["checks"]], [0, 5, 7, 11, 50])

    def test_invalid_message_is_rejected(self):
        key = toy_rsa_keypair(61, 53, 17)
        with self.assertRaises(ValueError):
            encrypt(key.modulus, key)
        with self.assertRaises(ValueError):
            mod_pow(2, -1, 7)

    def test_key_generation_rejects_nonprime_and_invalid_exponents(self):
        with self.assertRaises(ValueError):
            toy_rsa_keypair(4, 11, 3)
        with self.assertRaises(ValueError):
            toy_rsa_keypair(5, 11, 1)
        with self.assertRaises(ValueError):
            toy_rsa_keypair(5, 11, 4)

    def test_raw_rsa_exposes_deterministic_and_multiplicative_structure(self):
        key = toy_rsa_keypair(61, 53, 17)
        self.assertEqual(raw_rsa_properties(2, 3, key), {"deterministic": True, "multiplicative": True})


if __name__ == "__main__":
    unittest.main()
