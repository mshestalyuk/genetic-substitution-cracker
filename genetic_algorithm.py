"""Minimal DEAP wiring example.

This is a OneMax smoke demo, not a cipher cracker yet. It exists to verify
that the project's evolutionary-algorithm dependencies are wired correctly.
"""

from __future__ import annotations

import random

from deap import algorithms, base, creator, tools

__all__ = ["run_demo"]


if not hasattr(creator, "WIPFitnessMax"):
    creator.create("WIPFitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "WIPIndividual"):
    creator.create("WIPIndividual", list, fitness=creator.WIPFitnessMax)


def _evaluate(individual: list[int]) -> tuple[int]:
    return (sum(individual),)


def run_demo(
    *,
    seed: int = 7,
    population_size: int = 20,
    genome_size: int = 12,
    generations: int = 5,
) -> dict[str, object]:
    """Run a tiny deterministic OneMax evolution and return its summary."""
    if min(population_size, genome_size, generations) < 1:
        raise ValueError("population_size, genome_size, and generations must be positive")

    state = random.getstate()
    random.seed(seed)
    try:
        toolbox = base.Toolbox()
        toolbox.register("bit", random.randint, 0, 1)
        toolbox.register(
            "individual",
            tools.initRepeat,
            creator.WIPIndividual,
            toolbox.bit,
            n=genome_size,
        )
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", _evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)

        population = toolbox.population(n=population_size)
        population, logbook = algorithms.eaSimple(
            population,
            toolbox,
            cxpb=0.5,
            mutpb=0.2,
            ngen=generations,
            verbose=False,
        )
        best = tools.selBest(population, k=1)[0]
        return {
            "best_individual": list(best),
            "best_fitness": best.fitness.values[0],
            "logbook": logbook,
        }
    finally:
        random.setstate(state)
