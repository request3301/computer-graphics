from __future__ import annotations

import random
import time

try:
    from .algorithms import (
        CIRCLE_ALGORITHMS,
        LINE_ALGORITHMS,
        CircleAlgorithm,
        LineAlgorithm,
    )
except ImportError:  # pragma: no cover - allows running as script
    from algorithms import (
        CIRCLE_ALGORITHMS,
        LINE_ALGORITHMS,
        CircleAlgorithm,
        LineAlgorithm,
    )


def run_benchmarks(
    line_algorithms: dict[str, dict[str, object]],
    circle_algorithms: dict[str, dict[str, object]],
    seed: int = 2025,
    line_tests: int = 4000,
    circle_tests: int = 2500,
) -> list[dict[str, float | str | int]]:
    rng = random.Random(seed)
    line_dataset = [
        (
            rng.randint(-60, 60),
            rng.randint(-60, 60),
            rng.randint(-60, 60),
            rng.randint(-60, 60),
        )
        for _ in range(line_tests)
    ]
    circle_dataset = [
        (
            rng.randint(-30, 30),
            rng.randint(-30, 30),
            rng.randint(1, 30),
        )
        for _ in range(circle_tests)
    ]

    results: list[dict[str, float | str | int]] = []
    for key, meta in line_algorithms.items():
        func: LineAlgorithm = meta["func"]  # type: ignore[assignment]
        start = time.perf_counter()
        for args in line_dataset:
            func(*args)
        elapsed_ms = (time.perf_counter() - start) * 1000
        avg_us = (elapsed_ms / line_tests) * 1000
        results.append(
            {
                "name": meta["label"],
                "tests": line_tests,
                "total": elapsed_ms,
                "avg": avg_us,
            }
        )

    for key, meta in circle_algorithms.items():
        func: CircleAlgorithm = meta["func"]  # type: ignore[assignment]
        start = time.perf_counter()
        for args in circle_dataset:
            func(*args)
        elapsed_ms = (time.perf_counter() - start) * 1000
        avg_us = (elapsed_ms / circle_tests) * 1000
        results.append(
            {
                "name": meta["label"],
                "tests": circle_tests,
                "total": elapsed_ms,
                "avg": avg_us,
            }
        )

    return results


def run_benchmarks_default() -> list[dict[str, float | str | int]]:
    return run_benchmarks(LINE_ALGORITHMS, CIRCLE_ALGORITHMS)


def main() -> None:
    print("Running performance benchmarks...")
    print("=" * 70)
    results = run_benchmarks_default()

    print(f"{'Algorithm':<30} {'Tests':<10} {'Total (ms)':<15} {'Avg (µs)':<15}")
    print("-" * 70)

    for record in results:
        name = str(record["name"])
        tests = int(record["tests"])
        total = float(record["total"])
        avg = float(record["avg"])
        print(f"{name:<30} {tests:<10} {total:<15.2f} {avg:<15.2f}")

    print("=" * 70)


if __name__ == "__main__":
    main()
