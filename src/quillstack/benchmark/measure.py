"""Measuring one implementation against another, in this process."""

from __future__ import annotations

import importlib.metadata
import statistics
import time
from collections.abc import Callable, Mapping

from quillstack.benchmark.errors import NotEnoughRepeatsError, NothingHappenedError
from quillstack.benchmark.result import Comparison, Measurement

MINIMUM_REPEATS = 3


def compare(
    cases: Mapping[str, Callable[[], object]],
    runs: int = 1000,
    repeats: int = 5,
    versions: Mapping[str, str] | None = None,
) -> Comparison:
    """Runs every case the same number of times, interleaved, and takes the middle result.

    Interleaved because a machine which gets busy halfway through would otherwise become the
    result: measuring all of A and then all of B blames B for whatever else the machine started
    doing. A, B, A, B spreads that across both.

    The median rather than the mean, because one slow repeat is noise and the mean believes it.

    Each case is called once before the clock starts, so what is measured is the work rather
    than whatever the first call imported.
    """
    if repeats < MINIMUM_REPEATS:
        raise NotEnoughRepeatsError(
            f"{repeats} repeats is not a median. Three is the fewest that can be one."
        )

    if runs < 1:
        raise NothingHappenedError(f"{runs} runs is not a measurement of anything.")

    if not cases:
        raise NothingHappenedError("Nothing to compare.")

    for run in cases.values():
        run()

    timings: dict[str, list[float]] = {name: [] for name in cases}

    for _ in range(repeats):
        # One pass over every case, then the next pass. This is the interleaving.
        for name, run in cases.items():
            timings[name].append(_batch(run, runs))

    measurements = [
        Measurement(
            name=name,
            median=statistics.median(values),
            runs=runs,
            version=(versions or {}).get(name) or _version(name),
        )
        for name, values in timings.items()
    ]

    return Comparison(
        measurements=measurements,
        unit="Per call",
        versions={m.name: m.version for m in measurements if m.version},
    )


def _batch(run: Callable[[], object], runs: int) -> float:
    start = time.perf_counter()

    for _ in range(runs):
        run()

    return time.perf_counter() - start


def _version(name: str) -> str | None:
    """The version of the distribution a case is named after, where it is named after one.

    Read from what is installed rather than from memory, which is the only way a version in a
    README is worth printing.
    """
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None
