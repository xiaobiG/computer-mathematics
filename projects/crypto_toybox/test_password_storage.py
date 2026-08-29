import unittest

from projects.crypto_toybox.password_storage import (
    ALGORITHM,
    PasswordRecord,
    make_password_record,
    migrate_after_successful_login,
    verify_password,
)


class PasswordStorageTests(unittest.TestCase):
    def test_unique_salts_make_same_password_records_different_and_verifiable(self):
        first = make_password_record("demo-password", rounds=1_000, salt=b"a" * 16)
        second = make_password_record("demo-password", rounds=1_000, salt=b"b" * 16)
        self.assertNotEqual(first.salt, second.salt)
        self.assertNotEqual(first.derived_key, second.derived_key)
        self.assertTrue(verify_password("demo-password", first))
        self.assertFalse(verify_password("wrong-password", first))

    def test_migration_requires_a_successful_login_and_raises_cost(self):
        old = make_password_record("demo-password", rounds=1_000, salt=b"a" * 16)
        self.assertIsNone(migrate_after_successful_login("wrong-password", old, target_rounds=2_000))
        upgraded = migrate_after_successful_login(
            "demo-password", old, target_rounds=2_000, salt=b"b" * 16,
        )
        self.assertIsNotNone(upgraded)
        assert upgraded is not None
        self.assertEqual(upgraded.algorithm, ALGORITHM)
        self.assertEqual(upgraded.rounds, 2_000)
        self.assertTrue(verify_password("demo-password", upgraded))
        self.assertIs(migrate_after_successful_login("demo-password", upgraded, target_rounds=2_000), upgraded)

    def test_invalid_record_and_parameter_contracts_are_rejected(self):
        with self.assertRaises(ValueError):
            make_password_record("", rounds=1_000)
        with self.assertRaises(ValueError):
            make_password_record("password", rounds=0)
        with self.assertRaises(ValueError):
            make_password_record("password", rounds=1_000, salt=b"short")
        with self.assertRaises(ValueError):
            verify_password("password", PasswordRecord("unknown", 1_000, b"a" * 16, b"x" * 32))
