import random
import unittest
from string import ascii_lowercase

try:
    from genetic_algorithm import (
        KEY_LENGTH,
        build_toolbox,
        decrypt,
        decryption_key_from_encryption_key,
        random_key,
    )
except ModuleNotFoundError as error:
    if error.name == "deap":
        build_toolbox = None
    else:
        raise

from ngram import NgramModel
from tests.sample_text import SAMPLE_TEXT

PLAINTEXT = "The keeper held a lantern in the window until the boats were safe."


def _encrypt(text, encryption_key):
    table = str.maketrans(
        ascii_lowercase + ascii_lowercase.upper(),
        encryption_key + encryption_key.upper(),
    )
    return text.translate(table)


def _is_permutation(key):
    return sorted(key) == list(range(KEY_LENGTH))


@unittest.skipIf(build_toolbox is None, "install requirements.txt to run DEAP tests")
class KeyRepresentationTests(unittest.TestCase):
    def setUp(self):
        rng = random.Random(42)
        self.encryption_key = "".join(rng.sample(ascii_lowercase, 26))
        self.ciphertext = _encrypt(PLAINTEXT, self.encryption_key)
        self.true_key = decryption_key_from_encryption_key(self.encryption_key)

    def test_true_key_recovers_plaintext(self):
        self.assertEqual(decrypt(self.ciphertext, self.true_key), PLAINTEXT)

    def test_identity_key_is_noop(self):
        self.assertEqual(decrypt("Abc, xyz!", list(range(26))), "Abc, xyz!")

    def test_bad_encryption_key_rejected(self):
        with self.assertRaises(ValueError):
            decryption_key_from_encryption_key("abc")

    def test_random_key_is_permutation(self):
        self.assertTrue(_is_permutation(random_key(random.Random(1))))


@unittest.skipIf(build_toolbox is None, "install requirements.txt to run DEAP tests")
class ToolboxTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = NgramModel.from_text(SAMPLE_TEXT, n=3)
        encryption_key = "".join(random.Random(7).sample(ascii_lowercase, 26))
        cls.ciphertext = _encrypt(PLAINTEXT, encryption_key)
        cls.true_key = decryption_key_from_encryption_key(encryption_key)

    def setUp(self):
        random.seed(0)
        self.toolbox = build_toolbox(self.ciphertext, self.model)

    def test_population_contains_valid_keys(self):
        population = self.toolbox.population(n=30)
        self.assertEqual(len(population), 30)
        self.assertTrue(all(_is_permutation(ind) for ind in population))

    def test_operators_preserve_permutations(self):
        for crossover in ("ordered", "pmx"):
            with self.subTest(crossover=crossover):
                toolbox = build_toolbox(self.ciphertext, self.model, crossover=crossover)
                population = toolbox.population(n=20)
                for _ in range(200):
                    a, b = random.sample(population, 2)
                    child1, child2 = toolbox.mate(toolbox.clone(a), toolbox.clone(b))
                    (mutant,) = toolbox.mutate(child1)
                    self.assertTrue(_is_permutation(mutant))
                    self.assertTrue(_is_permutation(child2))

    def test_true_key_beats_random_keys(self):
        (true_score,) = self.toolbox.evaluate(self.true_key)
        random_scores = [self.toolbox.evaluate(ind)[0] for ind in self.toolbox.population(n=50)]
        self.assertGreater(true_score, max(random_scores))

    def test_selection_returns_requested_count(self):
        population = self.toolbox.population(n=10)
        for ind in population:
            ind.fitness.values = self.toolbox.evaluate(ind)
        self.assertEqual(len(self.toolbox.select(population, k=10)), 10)

    def test_invalid_arguments_rejected(self):
        with self.assertRaises(ValueError):
            build_toolbox(self.ciphertext, self.model, crossover="nope")
        with self.assertRaises(ValueError):
            build_toolbox("ab", self.model)


if __name__ == "__main__":
    unittest.main()
