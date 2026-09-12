import unittest

from projects.crypto_toybox.main import toy_rsa_keypair, toy_rsa_sign, toy_rsa_verify


class ToySignatureTests(unittest.TestCase):
    def setUp(self):
        self.key = toy_rsa_keypair(61, 53, 17)

    def test_private_exponent_signature_verifies_with_public_exponent(self):
        signature = toy_rsa_sign(65, self.key)
        self.assertTrue(toy_rsa_verify(65, signature, self.key))

    def test_changed_representative_or_signature_is_rejected(self):
        signature = toy_rsa_sign(65, self.key)
        self.assertFalse(toy_rsa_verify(66, signature, self.key))
        self.assertFalse(toy_rsa_verify(65, (signature + 1) % self.key.modulus, self.key))

    def test_out_of_range_inputs_are_not_signable_or_verifiable(self):
        with self.assertRaises(ValueError):
            toy_rsa_sign(self.key.modulus, self.key)
        self.assertFalse(toy_rsa_verify(self.key.modulus, 1, self.key))
