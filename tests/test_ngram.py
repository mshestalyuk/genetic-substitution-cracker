import math
import tempfile
import unittest
from pathlib import Path

from corpus import normalize
from ngram import NgramModel
from tests.sample_text import SAMPLE_TEXT


class NgramModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = NgramModel.from_text(SAMPLE_TEXT, n=4)

    def test_counts_overlapping_ngrams(self):
        model = NgramModel.from_text("abcab", n=2)
        self.assertEqual(model.counts, {"ab": 2, "bc": 1, "ca": 1})

    def test_probabilities_sum_to_one(self):
        total = sum(10 ** model_lp for model_lp in self.model._log_probs.values())
        self.assertAlmostEqual(total, 1.0, places=9)

    def test_unseen_ngram_gets_floor(self):
        self.assertEqual(self.model.log_prob("qqqq"), self.model.floor)
        self.assertLess(self.model.floor, min(self.model._log_probs.values()))

    def test_language_scores_higher_than_gibberish(self):
        english = normalize("the keeper walked down to the harbour in the morning")
        gibberish = normalize("xqzv jwkp fhgm rtyb nnqx zzvk plmw qhjx vbnr tkdf")
        self.assertGreater(
            self.model.score_per_ngram(english), self.model.score_per_ngram(gibberish)
        )

    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp, "model.json")
            self.model.save(path)
            loaded = NgramModel.load(path)
        self.assertEqual(loaded.n, 4)
        self.assertEqual(loaded.counts, self.model.counts)
        self.assertTrue(math.isclose(loaded.floor, self.model.floor))

    def test_rejects_empty_or_bad_input(self):
        with self.assertRaises(ValueError):
            NgramModel.from_text("ab", n=4)
        with self.assertRaises(ValueError):
            NgramModel({"abc": 1}, n=4)


if __name__ == "__main__":
    unittest.main()
