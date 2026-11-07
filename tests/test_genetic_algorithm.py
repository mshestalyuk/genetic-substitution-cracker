import unittest


class GeneticAlgorithmTests(unittest.TestCase):
    def test_demo_runs_and_returns_a_fitness(self):
        result = run_demo(seed=1, population_size=8, genome_size=6, generations=2)
        self.assertEqual(len(result["best_individual"]), 6)
        self.assertGreaterEqual(result["best_fitness"], 0)

    def test_demo_is_repeatable_for_a_seed(self):
        first = run_demo(seed=3)
        second = run_demo(seed=3)
        self.assertEqual(first["best_individual"], second["best_individual"])


if __name__ == "__main__":
    unittest.main()
