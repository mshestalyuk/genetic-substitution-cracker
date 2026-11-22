# Genetic substitution cracker

This repository is experimenting with genetic
algorithms and classical substitution ciphers.

## Modules

- `cipher.py` – Caesar and monoalphabetic substitution ciphers.
- `corpus.py` – downloads Wolne Lektury / Project Gutenberg texts, strips
  license boilerplate and normalizes to `a-z` (Polish diacritics folded).
- `ngram.py` – n-gram language model; scores how "language-like" a text is.
- `genetic_algorithm.py` – substitution keys as DEAP permutation individuals,
  with OX/PMX crossover, swap mutation and n-gram fitness.

## Run locally

```text
python -m venv .venv
```

Activate the virtual environment using the command appropriate for your
operating system, then install dependencies:

```text
python -m pip install -r requirements.txt
python -m unittest discover
python main.py
```

The cipher module itself uses only the Python standard library. DEAP is
required for the genetic-algorithm code and its tests.

## Corpus and n-gram model

Fetch books by Wolne Lektury slug (or any full `.txt` URL), then build a
quadgram model:

```text
python corpus.py fetch pan-tadeusz lalka-tom-pierwszy quo-vadis
python corpus.py stats
python ngram.py build --n 4 --out data/pl_quadgrams.json
python ngram.py score data/pl_quadgrams.json "Litwo! Ojczyzno moja!"
```

Everything under `data/` is git- and docker-ignored.

## Docker

```text
docker build -t gsc .
docker run --rm gsc                                   # run tests (default)
docker run --rm gsc python main.py                    # cipher demo
docker run --rm -v "$PWD/data:/app/data" gsc python corpus.py fetch pan-tadeusz
docker run --rm -v "$PWD/data:/app/data" gsc python ngram.py build --out data/pl_quadgrams.json
```

Mount `./data` so downloaded corpora and models survive between runs.
