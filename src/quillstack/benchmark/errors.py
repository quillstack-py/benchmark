"""What this refuses to measure."""

from __future__ import annotations


class BenchmarkError(Exception):
    """Everything here raises this, or something which is one."""


class NotEnoughRepeatsError(BenchmarkError):
    """One run of each is an anecdote.

    A busy machine is enough to reverse a result, and the answer to that is to run it several
    times and take the middle one. Fewer than three is not a median, so it is refused rather
    than reported.
    """


class NothingHappenedError(BenchmarkError):
    """A batch which was asked to do nothing.

    The PHP benchmark package once reported timings of zero because it shelled out to a
    `python` which was not on the machine: the command failed instantly, and instantly is fast.
    A number like that is a mistake, and the only useful thing to do with it is refuse it.

    Asking how many runs there were catches it and asking how long they took does not — a
    threshold on the clock says different things under a profiler than without one, and a rule
    which depends on how fast the machine is, is not a rule.
    """
