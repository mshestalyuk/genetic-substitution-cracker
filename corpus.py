"""Corpus loading and text normalization.

Texts from Wolne Lektury and Project Gutenberg are cleaned of their
license boilerplate and reduced to the 26-letter Latin alphabet, so that
the n-gram model, the cipher and the GA all work on the same symbols.

Polish diacritics are folded to their base letters (ą→a, ł→l, ż→z, ...).
This matches ``cipher.py``, which only substitutes ``a-z``.

Download books (needs network access)::

    python corpus.py fetch pan-tadeusz lalka-tom-pierwszy
    python corpus.py fetch https://www.gutenberg.org/ebooks/1342.txt.utf-8
"""

from __future__ import annotations

import argparse
import re
import unicodedata
from collections.abc import Iterable
from pathlib import Path
from string import ascii_lowercase
from urllib.parse import urlparse
from urllib.request import Request, urlopen

__all__ = [
    "ALPHABET",
    "normalize",
    "strip_boilerplate",
    "load_corpus",
    "download",
    "resolve_source",
]

ALPHABET = ascii_lowercase
DEFAULT_CORPUS_DIR = Path("data/corpus")
WOLNE_LEKTURY_TXT = "https://wolnelektury.pl/media/book/txt/{slug}.txt"

# Letters that NFKD does not decompose into "base letter + combining mark".
_UNDECOMPOSABLE = str.maketrans(
    {"ł": "l", "Ł": "L", "ß": "ss", "æ": "ae", "Æ": "AE", "ø": "o", "Ø": "O",
     "œ": "oe", "Œ": "OE", "đ": "d", "Đ": "D"}
)
_NOT_LETTER = re.compile(f"[^{ALPHABET}]+")
_GUTENBERG_START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
_GUTENBERG_END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG", re.I)
_WOLNE_LEKTURY_FOOTER = re.compile(r"^-----\s*$", re.M)


def fold_diacritics(text: str) -> str:
    """Replace accented letters with their ASCII base letters."""
    decomposed = unicodedata.normalize("NFKD", text.translate(_UNDECOMPOSABLE))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize(text: str, *, keep_spaces: bool = False) -> str:
    """Lowercase, fold diacritics and keep only ``a-z``.

    With ``keep_spaces=True`` every run of non-letters becomes one space,
    which is handy for showing results; scoring uses the letters-only form.
    """
    folded = fold_diacritics(text).lower()
    if keep_spaces:
        return _NOT_LETTER.sub(" ", folded).strip()
    return _NOT_LETTER.sub("", folded)


def strip_boilerplate(text: str) -> str:
    """Remove Project Gutenberg / Wolne Lektury license headers and footers."""
    start = _GUTENBERG_START.search(text)
    if start:
        text = text[start.end():]
        end = _GUTENBERG_END.search(text)
        if end:
            text = text[: end.start()]
        return text

    # Wolne Lektury .txt files end with a "-----" line followed by the
    # license note and credits. Cut at the last such line.
    footers = list(_WOLNE_LEKTURY_FOOTER.finditer(text))
    if footers and "wolnelektury" in text[footers[-1].end():].lower():
        text = text[: footers[-1].start()]
    return text


def _iter_text_files(paths: Iterable[str | Path]) -> Iterable[Path]:
    for path in map(Path, paths):
        if path.is_dir():
            yield from sorted(path.glob("*.txt"))
        elif path.is_file():
            yield path
        else:
            raise FileNotFoundError(f"Corpus path not found: {path}")


def load_corpus(paths: Iterable[str | Path] = (DEFAULT_CORPUS_DIR,)) -> str:
    """Read ``.txt`` files (or directories of them) into one normalized string."""
    files = list(_iter_text_files(paths))
    if not files:
        raise FileNotFoundError("No .txt files found; run `python corpus.py fetch ...` first")
    parts = [normalize(strip_boilerplate(f.read_text(encoding="utf-8"))) for f in files]
    return "".join(parts)


def resolve_source(source: str) -> str:
    """Turn a Wolne Lektury slug (e.g. ``pan-tadeusz``) into a URL."""
    if urlparse(source).scheme in {"http", "https"}:
        return source
    return WOLNE_LEKTURY_TXT.format(slug=source)


def download(source: str, dest_dir: str | Path = DEFAULT_CORPUS_DIR, *, timeout: float = 30) -> Path:
    """Download one book as UTF-8 text into ``dest_dir`` and return its path."""
    url = resolve_source(source)
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = Path(urlparse(url).path).name.removesuffix(".utf-8")
    target = dest_dir / (name if name.endswith(".txt") else f"{name}.txt")

    request = Request(url, headers={"User-Agent": "genetic-substitution-cracker/0.1"})
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - user-supplied corpus URL
        target.write_bytes(response.read())
    return target


def _main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    fetch = sub.add_parser("fetch", help="download books (Wolne Lektury slugs or URLs)")
    fetch.add_argument("sources", nargs="+")
    fetch.add_argument("--dest", default=DEFAULT_CORPUS_DIR, type=Path)

    stats = sub.add_parser("stats", help="show size of the normalized corpus")
    stats.add_argument("paths", nargs="*", default=[DEFAULT_CORPUS_DIR], type=Path)

    args = parser.parse_args()
    if args.command == "fetch":
        for source in args.sources:
            print(f"saved {download(source, args.dest)}")
    else:
        text = load_corpus(args.paths)
        print(f"{len(text):,} letters; sample: {text[:60]}...")


if __name__ == "__main__":
    _main()
