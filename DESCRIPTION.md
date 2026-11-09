Project 5: Automated Cryptanalysis of Substitution Ciphers Using Genetic Algorithms

Description and Research Objective:
Implementation of a genetic algorithm in Python (using the DEAP framework) for
the evolutionary search of a substitution cipher key based on language n-gram
frequency matching.

Formal Threat Model:
Ciphertext-Only Attack (COA). Possession of ciphertext without knowledge of the
substitution alphabet key.

Scenario / Context:
Automation of message decryption in classical cryptanalysis tasks and Capture
The Flag (CTF) challenges.

Implementation Stages (Phases):

1. Generation of substitution ciphertexts;
2. Creation of an n-gram-based fitness function;
3. Configuration of crossover and mutation operators in DEAP;
4. Evolutionary recovery of the plaintext.

Attack Benchmark / Criterion:
Recovery of the plaintext with a character accuracy of > 95% for a ciphertext of 500 characters.

Dataset & Link:
Texts from the open digital library Wolne Lektury / Project Gutenberg –
https://wolnelektury.pl

Scientific Literature (IEEE/APA):

  - Picek, S. et al. (2016). Evolutionary algorithms for cryptanalysis: A
    survey. Applied Soft Computing.
  - Fortuna, S. (2021). DEAP: Distributed Evolutionary Algorithms in Python.
    GitHub Repository.
  - Project Gutenberg (2024). Free ebooks repository. https://www.gutenberg.org
