"""Measuring what somebody actually pays, which is the whole process."""

from __future__ import annotations

import statistics
import subprocess
import sys
import time
from collections.abc import Mapping

from quillstack.benchmark.errors import NotEnoughRepeatsError, NothingHappenedError
from quillstack.benchmark.measure import MINIMUM_REPEATS, _version
from quillstack.benchmark.result import Comparison, Measurement

BARE = "the interpreter, importing nothing"


def compare_processes(
    cases: Mapping[str, str],
    runs: int = 25,
    repeats: int = 5,
    versions: Mapping[str, str] | None = None,
    baseline: bool = True,
) -> Comparison:
    """Runs each case as its own process, and says how long the whole thing took.

    A per-call figure with the importing amortised away answers how expensive the work is. This
    answers what somebody waits for, which is a different question and often a different
    answer: a library fourteen times slower per call can be six milliseconds slower at boot.

    The baseline row is the interpreter starting and importing nothing. Without it a reader
    cannot tell how much of the wait was the language rather than anything either case did,
    and for a short program that is most of it.
    """
    if repeats < MINIMUM_REPEATS:
        raise NotEnoughRepeatsError(
            f"{repeats} repeats is not a median. Three is the fewest that can be one."
        )

    if runs < 1:
        raise NothingHappenedError(f"{runs} runs is not a measurement of anything.")

    everything = {BARE: "pass", **cases} if baseline else dict(cases)
    timings: dict[str, list[float]] = {name: [] for name in everything}

    for _ in range(repeats):
        for name, source in everything.items():
            timings[name].append(_batch(source, runs))

    measured = {
        name: Measurement(
            name=name,
            median=statistics.median(values),
            runs=runs,
            version=(versions or {}).get(name) or _version(name),
        )
        for name, values in timings.items()
    }

    return Comparison(
        measurements=[m for name, m in measured.items() if name != BARE],
        unit="Whole process",
        baseline=measured.get(BARE),
        versions={m.name: m.version for m in measured.values() if m.version},
    )


def _batch(source: str, runs: int) -> float:
    start = time.perf_counter()

    for _ in range(runs):
        # check=True, so a case which fails to run is an error rather than a fast result.
        subprocess.run([sys.executable, "-c", source], check=True, capture_output=True)

    return time.perf_counter() - start
