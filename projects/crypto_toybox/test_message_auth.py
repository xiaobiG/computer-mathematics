import unittest

from projects.crypto_toybox.message_auth import (
    encode_sequenced_message,
    hmac_tag,
    sequenced_hmac_tag,
    verify_hmac,
    verify_sequenced_hmac,
)


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

    def test_length_prefixed_encoding_separates_previously_ambiguous_fields(self):
        self.assertNotEqual(
            encode_sequenced_message(1, b"ab") + b"c",
            encode_sequenced_message(1, b"a") + b"bc",
        )

    def test_valid_tag_is_still_rejected_when_the_sequence_is_replayed(self):
        key, payload = b"demo-shared-key", b"amount=100"
        tag = sequenced_hmac_tag(key, 7, payload)
        fresh = verify_sequenced_hmac(key, 7, payload, tag, last_accepted_sequence=6)
        replay = verify_sequenced_hmac(key, 7, payload, tag, last_accepted_sequence=7)
        self.assertTrue(fresh.accepted)
        self.assertTrue(replay.tag_valid)
        self.assertFalse(replay.sequence_is_fresh)
        self.assertFalse(replay.accepted)

    def test_sequenced_verification_rejects_tampering_and_invalid_sequence_contracts(self):
        key, payload = b"demo-shared-key", b"amount=100"
        tag = sequenced_hmac_tag(key, 7, payload)
        self.assertFalse(verify_sequenced_hmac(key, 7, b"amount=900", tag, last_accepted_sequence=6).accepted)
        with self.assertRaises(ValueError):
            sequenced_hmac_tag(key, -1, payload)


if __name__ == "__main__":
    unittest.main()
