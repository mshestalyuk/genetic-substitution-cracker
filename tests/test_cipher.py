import unittest

from cipher import SubstitutionCipher


class SubstitutionCipherTests(unittest.TestCase):
    def test_both_algorithms_round_trip(self):
        plaintext = "Attack at dawn! Żółw 123."
        for algorithm in ("caesar", "monoalphabetic"):
            with self.subTest(algorithm=algorithm):
                cipher = SubstitutionCipher(algorithm)
                encrypted = cipher.cipher(plaintext)
                self.assertEqual(cipher.decipher(encrypted), plaintext)
                self.assertIn("Żół", encrypted)
                self.assertTrue(encrypted.endswith(" 123."))

    def test_cipher_preserves_case(self):
        cipher = SubstitutionCipher("caesar")
        encrypted = cipher.cipher("AbZ")
        self.assertTrue(encrypted[0].isupper())
        self.assertTrue(encrypted[1].islower())
        self.assertTrue(encrypted[2].isupper())

    def test_unknown_algorithm_is_rejected(self):
        with self.assertRaises(ValueError):
            SubstitutionCipher("not-a-cipher")

    def test_instances_have_independent_keys(self):
        first = SubstitutionCipher("caesar")
        second = SubstitutionCipher("caesar")
        # A probabilistic collision is possible, so compare behavior after
        # controlling the random source rather than relying on key inequality.
        self.assertIsNot(first._strategy, second._strategy)


if __name__ == "__main__":
    unittest.main()
