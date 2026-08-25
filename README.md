# Quillstack Benchmark

[![Tests](https://github.com/quillstack-py/benchmark/actions/workflows/tests.yml/badge.svg)](https://github.com/quillstack-py/benchmark/actions/workflows/tests.yml)
[![Latest Version](https://img.shields.io/pypi/v/quillstack-benchmark.svg)](https://pypi.org/project/quillstack-benchmark/)
[![Downloads](https://img.shields.io/pypi/dm/quillstack-benchmark.svg)](https://pypi.org/project/quillstack-benchmark/)
[![Python Version](https://img.shields.io/pypi/pyversions/quillstack-benchmark)](https://pypi.org/project/quillstack-benchmark/)
[![CodeFactor](https://www.codefactor.io/repository/github/quillstack-py/benchmark/badge)](https://www.codefactor.io/repository/github/quillstack-py/benchmark)
[![Quality Gate](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_benchmark&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=quillstack-py_benchmark)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_benchmark&metric=coverage)](https://sonarcloud.io/summary/new_code?id=quillstack-py_benchmark)
[![Maintainability](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_benchmark&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_benchmark)
[![Reliability](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_benchmark&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_benchmark)
[![Security](https://sonarcloud.io/api/project_badges/measure?project=quillstack-py_benchmark&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=quillstack-py_benchmark)
[![License](https://img.shields.io/pypi/l/quillstack-benchmark)](https://github.com/quillstack-py/benchmark/blob/main/LICENSE)

Measures one implementation against another, and writes the table.

## Why this exists

**It is not a timer.** `time.perf_counter` is a timer, `timeit` is a timer, and there is no
reason to write a third. What this holds is the part that gets forgotten: the discipline a
measurement needs before it is evidence.

Every benchmark in this project was hand-rolled before this existed, and each time the same four
things had to be remembered — interleave the runs, take a median, measure the whole as well as
the part, and read the versions from what is installed. Four times out of five that is fine. The
fifth is a number in a README that nobody can reproduce.

So the rules are what the package is:

- **The runs are interleaved.** A, B, A, B rather than all of A and then all of B. Measuring one
  and then the other blames the second for whatever else the machine started doing halfway
  through.
- **A median, not one go.** Fewer than three repeats is refused rather than reported, because
  fewer than three cannot have a middle.
- **A batch which was asked to do nothing is an error.** The PHP benchmark package once reported
  timings of zero, having shelled out to a `python` which was not on the machine: the command
  failed instantly, and instantly is fast. Asking how many runs there were catches that; asking
  how long they took does not, because a threshold on the clock says one thing under a profiler
  and another without one.
- **The versions are read from what is installed**, never from memory.
- **The whole is measured as well as the part**, and the whole says how much of itself was the
  interpreter starting.

## Requirements

- Python 3.11 or newer

## Installation

```shell
pip install quillstack-benchmark
```

## Usage

```python
from quillstack.benchmark import compare

print(compare(
    {
        "quillstack-dotenv": lambda: Dotenv("app.env").load(),
        "python-dotenv": lambda: dotenv_values("app.env"),
    },
    runs=1000,
))
```

```text
| | Version |
| --- | --- |
| python-dotenv | 1.2.3 |
| quillstack-dotenv | 0.1.1 |

| | Per call | Relative |
| --- | --- | --- |
| **quillstack-dotenv** | **33.4 µs** | — |
| python-dotenv | 493.1 µs | 14.7× |
```

That is markdown, because the next thing that happens to it is being pasted into a README.

### What somebody actually waits for

A per-call figure has the importing amortised away, which answers how expensive the work is.
It does not answer what anybody pays. For that, measure the whole process:

```python
from quillstack.benchmark import compare_processes

print(compare_processes(
    {
        "quillstack-dotenv": "from quillstack.dotenv import Dotenv; Dotenv('app.env').load()",
        "python-dotenv": "from dotenv import dotenv_values; dotenv_values('app.env')",
    },
    runs=25,
))
```

```text
| | Whole process | Of which is the library |
| --- | --- | --- |
| the interpreter, importing nothing | 16.50 ms | — |
| **quillstack-dotenv** | **22.88 ms** | **6.38 ms** |
| python-dotenv | 29.87 ms | 13.37 ms |
```

**The two tables say different things about the same pair.** Per call one is fifteen times the
other; at boot the difference is seven milliseconds, and more of the wait than either of them is
Python starting up. A benchmark which gives only the first is technically true and answers a
question nobody asked.

The baseline row is why the last column can exist, which is why it is not optional.

### What it will not do

```python
compare({"a": ..., "b": ...}, runs=1000, repeats=1)
```

```text
NotEnoughRepeatsError: 1 repeats is not a median. Three is the fewest that can be one.
```

```python
compare({"nothing": lambda: None}, runs=0)
```

```text
NothingHappenedError: 0 runs is not a measurement of anything.
```

A process which will not run is an error for the same reason, rather than a very fast result.

Neither of these is a number worth having, so neither is returned.

### What it does not know

Which one is better. It says how long they took, and the standard says to write what each does
that the other does not **above** the numbers rather than below them — because being faster
because you do less is not being faster.

## Benchmark

There is nothing to compare this against, and comparing it against `timeit` would be comparing
a harness to the thing it calls. What it adds to a measurement is a few microseconds of
bookkeeping around batches that take milliseconds.

## Tests

```shell
uv run pytest
```

### Static analysis

```shell
uv run ruff check --no-cache
uv run mypy
```

### Against the standard

```shell
uv run quillstack-standards .
```

## The rest of Quillstack

This is one component of [Quillstack](https://quillstack.org), the same way of building APIs in
more than one language.

- [quillstack-standards](https://github.com/quillstack-py/standards) — what keeps every package the same shape
- [quillstack-dotenv](https://github.com/quillstack-py/dotenv) — the first package measured with this
- [quillstack/benchmark](https://github.com/quillstack/benchmark) — the PHP one, which times whole commands and HTTP requests instead

## License

MIT — see [LICENSE](https://github.com/quillstack-py/benchmark/blob/main/LICENSE).
