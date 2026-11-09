from __future__ import annotations

import random
from abc import ABC, abstractmethod
from string import ascii_lowercase
from typing import Callable

__all__ = ["SubstitutionCipher"]


class _CipherStrategy(ABC):
    @abstractmethod
    def cipher(self, text: str) -> str:
        """Encrypt text."""

    @abstractmethod
    def decipher(self, text: str) -> str:
        """Decrypt text."""


def _substitute(text: str, alphabet: str, replacement: str) -> str:
    table = str.maketrans(alphabet + alphabet.upper(), replacement + replacement.upper())
    return text.translate(table)


class _CaesarStrategy(_CipherStrategy):
    def __init__(self) -> None:
        self._shift = random.randrange(len(ascii_lowercase))

    def cipher(self, text: str) -> str:
        shifted = ascii_lowercase[self._shift :] + ascii_lowercase[: self._shift]
        return _substitute(text, ascii_lowercase, shifted)

    def decipher(self, text: str) -> str:
        shifted = ascii_lowercase[self._shift :] + ascii_lowercase[: self._shift]
        return _substitute(text, shifted, ascii_lowercase)


class _MonoalphabeticStrategy(_CipherStrategy):
    def __init__(self) -> None:
        shuffled = list(ascii_lowercase)
        random.shuffle(shuffled)
        self._key = "".join(shuffled)

    def cipher(self, text: str) -> str:
        return _substitute(text, ascii_lowercase, self._key)

    def decipher(self, text: str) -> str:
        return _substitute(text, self._key, ascii_lowercase)


_STRATEGIES: dict[str, Callable[[], _CipherStrategy]] = {
    "caesar": _CaesarStrategy,
    "monoalphabetic": _MonoalphabeticStrategy,
}


class SubstitutionCipher:
    def __init__(self, algorithm: str) -> None:
        try:
            strategy_factory = _STRATEGIES[algorithm.lower()]
        except (AttributeError, KeyError) as error:
            supported = ", ".join(sorted(_STRATEGIES))
            raise ValueError(
                f"Unknown algorithm {algorithm!r}; choose one of: {supported}"
            ) from error
        self._strategy = strategy_factory()

    def cipher(self, text: str) -> str:
        return self._strategy.cipher(text)

    def decipher(self, text: str) -> str:
        return self._strategy.decipher(text)
