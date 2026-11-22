Next steps:
1. Expose the cipher key (or accept a seed) so generated ciphertexts can be scored against the truth.
2. Write the evolution loop (`crack(ciphertext, model)`): elitism, restarts, stop on stagnation.
3. Add letter-accuracy metric and a benchmark: N random 500-letter excerpts, report mean/median accuracy vs. the >95% criterion.
4. Tune: population size, generations, cxpb/mutpb, OX vs PMX, n=3 vs n=4; optional frequency-seeded initial population.
5. CLI in `main.py`: `crack`, `benchmark`; results as CSV/plots for the report.
