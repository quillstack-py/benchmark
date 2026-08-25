"""Measures one implementation against another.

Not a timer — `time.perf_counter` is a timer and it is already here. What this holds is the
discipline a measurement needs before it is evidence: interleaved runs so a busy machine does
not become the result, a median rather than one go, the whole cost as well as the part, and a
refusal to report a batch that finished too fast to have happened.
"""

from quillstack.benchmark.errors import BenchmarkError, NotEnoughRepeatsError, NothingHappenedError
from quillstack.benchmark.measure import compare
from quillstack.benchmark.processes import compare_processes
from quillstack.benchmark.result import Comparison, Measurement

__all__ = [
    "BenchmarkError",
    "Comparison",
    "Measurement",
    "NotEnoughRepeatsError",
    "NothingHappenedError",
    "compare",
    "compare_processes",
]
