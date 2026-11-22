"""Substitution keys as DEAP individuals.

Representation
--------------
An individual is a permutation of ``range(26)`` read as a *decryption* key:

    individual[j] == i   means   ciphertext letter ALPHABET[j] -> plaintext ALPHABET[i]

Permutation-safe operators keep every individual a valid key:

* crossover: ``tools.cxOrdered`` (OX) or ``tools.cxPartialyMatched`` (PMX)
* mutation:  ``tools.mutShuffleIndexes`` — swaps letter pairs
* selection: tournament

"""

import random
from collections.abc import Sequence

from deap import base, creator, tools

from corpus import ALPHABET, normalize
from ngram import NgramModel

__all__ = [
    "KEY_LENGTH",
    "key_to_string",
    "decrypt",
    "decryption_key_from_encryption_key",
    "random_key",
    "build_toolbox",
]

KEY_LENGTH = len(ALPHABET)

if not hasattr(creator, "KeyFitness"):
    creator.create("KeyFitness", base.Fitness, weights=(1.0,))
if not hasattr(creator, "KeyIndividual"):
    creator.create("KeyIndividual", list, fitness=creator.KeyFitness)

_CROSSOVERS = {"ordered": tools.cxOrdered, "pmx": tools.cxPartialyMatched}


def key_to_string(key: Sequence[int]) -> str:
    """Plaintext letters for ciphertext ``a..z``, e.g. ``'qwerty...'``."""
    return "".join(ALPHABET[i] for i in key)


def decrypt(ciphertext: str, key: Sequence[int]) -> str:
    """Apply a decryption key; keeps case and leaves non-letters untouched."""
    plain = key_to_string(key)
    table = str.maketrans(ALPHABET + ALPHABET.upper(), plain + plain.upper())
    return ciphertext.translate(table)


def decryption_key_from_encryption_key(encryption_key: str) -> list[int]:
    """Convert a ``cipher.py``-style key (plain ``a..z`` -> ``encryption_key``)."""
    if sorted(encryption_key) != list(ALPHABET):
        raise ValueError("encryption key must be a permutation of a-z")
    return [encryption_key.index(c) for c in ALPHABET]


def random_key(rng: random.Random | None = None) -> list[int]:
    return (rng or random).sample(range(KEY_LENGTH), KEY_LENGTH)


def build_toolbox(
    ciphertext: str,
    model: NgramModel,
    *,
    crossover: str = "ordered",
    swap_probability: float = 1 / KEY_LENGTH,
    tournament_size: int = 3,
) -> base.Toolbox:
    """Register population init, fitness and genetic operators for one ciphertext.

    DEAP operators use the global ``random`` module, so seed it before
    evolving if you need repeatable runs.
    """
    try:
        mate = _CROSSOVERS[crossover]
    except KeyError as error:
        raise ValueError(f"crossover must be one of {sorted(_CROSSOVERS)}") from error

    letters = normalize(ciphertext)
    if len(letters) < model.n:
        raise ValueError(f"ciphertext needs at least {model.n} letters")

    def evaluate(individual: Sequence[int]) -> tuple[float]:
        return (model.score(decrypt(letters, individual)),)

    toolbox = base.Toolbox()
    toolbox.register("indices", random.sample, range(KEY_LENGTH), KEY_LENGTH)
    toolbox.register("individual", tools.initIterate, creator.KeyIndividual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", mate)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=swap_probability)
    toolbox.register("select", tools.selTournament, tournsize=tournament_size)
    return toolbox
