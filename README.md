# Genetic substitution cracker

This repository is experimenting with genetic
algorithms and classical substitution ciphers.

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
required for the genetic-algorithm demo and its tests.