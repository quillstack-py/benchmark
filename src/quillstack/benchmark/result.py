"""What a comparison found, and how it is written down."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Measurement:
    """One case, measured."""

    name: str
    median: float
    """Seconds for the whole batch — the middle of the repeats, not the mean."""

    runs: int
    version: str | None = None
    note: str = ""

    @property
    def each(self) -> float:
        """Seconds for one call."""
        return self.median / self.runs


@dataclass
class Comparison:
    """Every case, and the table it makes.

    The fastest is not called the winner anywhere in here. Which one is better is a question
    about what each does, and this only knows how long they took.
    """

    measurements: list[Measurement]
    unit: str = "per call"
    baseline: Measurement | None = None
    """The interpreter doing nothing, where the whole process was measured. Without it a reader
    cannot tell how much of the wait was anything either library did."""

    versions: dict[str, str] = field(default_factory=dict)

    def fastest(self) -> Measurement:
        return min(self.measurements, key=lambda m: m.median)

    def table(self) -> str:
        """The markdown to paste into a README."""
        fastest = self.fastest()

        # Where there is a baseline, what a reader wants is the part that was the library, not
        # the total — most of a short program's runtime is the interpreter starting, and a
        # column of totals hides that behind a ratio of nearly one.
        if self.baseline is not None:
            return self._against_baseline()

        rows = ["| | " + self.unit + " | Relative |", "| --- | --- | --- |"]

        for measurement in self.measurements:
            name = measurement.name
            each = _time(measurement.each)

            if measurement is fastest:
                rows.append(f"| **{name}** | **{each}** | — |")

                continue

            relative = measurement.median / fastest.median
            rows.append(f"| {name} | {each} | {relative:.1f}× |")

        return "\n".join(rows)

    def _against_baseline(self) -> str:
        assert self.baseline is not None
        bare = self.baseline.each
        fastest = min(self.measurements, key=lambda m: m.each - bare)

        rows = [
            f"| | {self.unit} | Of which is the library |",
            "| --- | --- | --- |",
            f"| {self.baseline.name} | {_time(bare)} | — |",
        ]

        for measurement in self.measurements:
            contribution = _time(max(measurement.each - bare, 0.0))
            whole = _time(measurement.each)

            if measurement is fastest:
                rows.append(f"| **{measurement.name}** | **{whole}** | **{contribution}** |")
            else:
                rows.append(f"| {measurement.name} | {whole} | {contribution} |")

        return "\n".join(rows)

    def versions_table(self) -> str:
        if not self.versions:
            return ""

        rows = ["| | Version |", "| --- | --- |"]
        rows += [f"| {name} | {version} |" for name, version in sorted(self.versions.items())]

        return "\n".join(rows)

    def __str__(self) -> str:
        parts = [self.versions_table(), self.table()]

        return "\n\n".join(part for part in parts if part)


def _time(seconds: float) -> str:
    """A duration in the unit somebody would say it in."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.0f} ns"

    if seconds < 1e-3:
        return f"{seconds * 1e6:.1f} µs"

    if seconds < 1:
        return f"{seconds * 1e3:.2f} ms"

    return f"{seconds:.2f} s"
