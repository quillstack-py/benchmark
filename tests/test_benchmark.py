"""What makes a measurement evidence rather than an anecdote."""

from __future__ import annotations

import subprocess
import time

import pytest

from quillstack.benchmark import (
    NotEnoughRepeatsError,
    NothingHappenedError,
    compare,
    compare_processes,
)
from quillstack.benchmark.result import Comparison, Measurement


def sleepy(seconds: float):  # type: ignore[no-untyped-def]
    def run() -> None:
        time.sleep(seconds)

    return run


def test_the_slower_case_is_reported_as_slower() -> None:
    result = compare({"quick": sleepy(0.0001), "slow": sleepy(0.001)}, runs=5, repeats=3)

    assert result.fastest().name == "quick"
    assert "quick" in result.table()
    assert "×" in result.table()


def test_one_run_of_each_is_not_a_median() -> None:
    """A busy machine is enough to reverse a result, and the answer is to run it several times
    and take the middle one. Fewer than three cannot be a middle."""
    with pytest.raises(NotEnoughRepeatsError, match="not a median"):
        compare({"a": lambda: None}, runs=10, repeats=1)

    with pytest.raises(NotEnoughRepeatsError):
        compare_processes({"a": "pass"}, runs=1, repeats=2)


def test_a_batch_which_did_not_happen_is_refused() -> None:
    """The PHP benchmark package once reported timings of zero, having shelled out to a
    `python` which was not on the machine: the command failed instantly, and instantly is fast.

    A measurement that fast is a mistake, and the only useful thing to do with it is say so.
    """
    with pytest.raises(NothingHappenedError, match="not a measurement"):
        compare({"nothing": lambda: None}, runs=0, repeats=3)

    with pytest.raises(NothingHappenedError, match="Nothing to compare"):
        compare({}, runs=10, repeats=3)

    with pytest.raises(NothingHappenedError, match="not a measurement"):
        compare_processes({"a": "pass"}, runs=0, repeats=3)


def test_every_case_is_run_the_same_number_of_times() -> None:
    counted = {"a": 0, "b": 0}

    def count(name: str):  # type: ignore[no-untyped-def]
        def run() -> None:
            counted[name] += 1

        return run

    compare({"a": count("a"), "b": count("b")}, runs=10, repeats=3)

    # One warm-up each, then three repeats of ten.
    assert counted["a"] == counted["b"] == 31


def test_the_version_is_read_from_what_is_installed() -> None:
    """A version in a README is worth printing only if it was read rather than remembered."""
    result = compare(
        {"pytest": lambda: None, "not-a-real-distribution": lambda: None}, runs=5, repeats=3
    )

    assert result.versions["pytest"]
    assert "not-a-real-distribution" not in result.versions


def test_a_whole_process_table_says_what_was_the_library() -> None:
    """Most of a short program's runtime is the interpreter starting.

    A table of totals hides that behind a ratio of nearly one, so where there is a baseline the
    column is what the library added rather than what the process took.
    """
    comparison = Comparison(
        measurements=[
            Measurement("fast", median=0.020, runs=1),
            Measurement("slow", median=0.030, runs=1),
        ],
        unit="Whole process",
        baseline=Measurement("the interpreter, importing nothing", median=0.015, runs=1),
    )

    table = comparison.table()

    assert "Of which is the library" in table
    assert "5.00 ms" in table
    assert "15.00 ms" in table


def test_a_process_which_will_not_run_is_an_error_rather_than_a_fast_result() -> None:
    with pytest.raises(subprocess.CalledProcessError):
        compare_processes({"broken": "raise SystemExit(1)"}, runs=1, repeats=3, baseline=False)


def test_durations_are_written_in_the_unit_somebody_would_say_them_in() -> None:
    from quillstack.benchmark.result import _time

    assert _time(0.0000000005) == "0 ns"
    assert _time(0.000_033_4) == "33.4 µs"
    assert _time(0.0228) == "22.80 ms"
    assert _time(1.5) == "1.50 s"
