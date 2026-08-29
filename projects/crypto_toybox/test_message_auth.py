import unittest

from projects.crypto_toybox.message_auth import hmac_tag, verify_hmac


class MessageAuthTests(unittest.TestCase):
    def test_valid_message_and_tag_verify(self):
        key, message = b"demo-shared-key", b"amount=100"
        self.assertTrue(verify_hmac(key, message, hmac_tag(key, message)))

    def test_tampering_message_or_tag_is_rejected(self):
        key, message = b"demo-shared-key", b"amount=100"
        tag = hmac_tag(key, message)
        self.assertFalse(verify_hmac(key, b"amount=900", tag))
        self.assertFalse(verify_hmac(key, message, tag[:-1] + b"x"))

    def test_empty_key_is_rejected(self):
        with self.assertRaises(ValueError):
            hmac_tag(b"", b"message")


if __name__ == "__main__":
    unittest.main()
