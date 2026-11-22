"""N-gram language model used as the GA fitness signal.

The model stores log10 probabilities of every n-gram seen in the corpus.
A candidate plaintext is scored as the sum of log-probabilities of its
overlapping n-grams; unseen n-grams get a small floor value. Higher (less
negative) scores mean "looks more like the training language".

Build and cache a model::

    python ngram.py build --n 4 --out data/pl_quadgrams.json
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

from corpus import DEFAULT_CORPUS_DIR, load_corpus, normalize

__all__ = ["NgramModel"]


class NgramModel:
    def __init__(self, counts: dict[str, int], n: int) -> None:
        if n < 1:
            raise ValueError("n must be positive")
        if not counts:
            raise ValueError("cannot build an n-gram model from zero n-grams")
        if any(len(gram) != n for gram in counts):
            raise ValueError(f"all n-grams must have length {n}")

        self.n = n
        self.counts = dict(counts)
        total = sum(self.counts.values())
        self._log_probs = {gram: math.log10(c / total) for gram, c in self.counts.items()}
        # Unseen n-grams are treated as ~1/100 of a single occurrence.
        self.floor = math.log10(0.01 / total)

    @classmethod
    def from_text(cls, text: str, n: int = 4) -> NgramModel:
        """Count overlapping n-grams in ``text`` (normalized here)."""
        letters = normalize(text)
        counts = Counter(letters[i : i + n] for i in range(len(letters) - n + 1))
        return cls(counts, n)

    def log_prob(self, gram: str) -> float:
        return self._log_probs.get(gram, self.floor)

    def score(self, letters: str) -> float:
        """Sum of n-gram log10 probabilities.

        ``letters`` must already be normalized (lowercase ``a-z`` only); the
        GA calls this thousands of times, so it skips re-normalizing.
        """
        n, get, floor = self.n, self._log_probs.get, self.floor
        return sum(get(letters[i : i + n], floor) for i in range(len(letters) - n + 1))

    def score_per_ngram(self, letters: str) -> float:
        """Length-independent score, useful for comparing texts of different size."""
        count = len(letters) - self.n + 1
        return self.score(letters) / count if count > 0 else self.floor

    def save(self, path: str | Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps({"n": self.n, "counts": self.counts}), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> NgramModel:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["counts"], data["n"])


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="build an n-gram model from the corpus")
    build.add_argument("--n", type=int, default=4)
    build.add_argument("--corpus", nargs="*", default=[DEFAULT_CORPUS_DIR], type=Path)
    build.add_argument("--out", type=Path, default=Path("data/quadgrams.json"))

    score = sub.add_parser("score", help="score a text with a saved model")
    score.add_argument("model", type=Path)
    score.add_argument("text")

    args = parser.parse_args()
    if args.command == "build":
        model = NgramModel.from_text(load_corpus(args.corpus), n=args.n)
        model.save(args.out)
        print(f"saved {len(model.counts):,} distinct {args.n}-grams to {args.out}")
    else:
        model = NgramModel.load(args.model)
        print(f"{model.score_per_ngram(normalize(args.text)):.3f} per n-gram")


if __name__ == "__main__":
    _main()
