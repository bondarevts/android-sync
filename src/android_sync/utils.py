from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class FileRecord:
    path: Path
    is_directory: bool


@dataclass(order=True)
class Month:
    year: int
    month: int

    def next(self) -> Month:
        if self.month < 12:
            return Month(self.year, self.month + 1)
        return Month(self.year + 1, 1)

    @staticmethod
    def segment(start: Month, end: Month) -> Iterable[Month]:
        current = start

        while current <= end:
            yield current
            current = current.next()


def get_month_name(month: int) -> str:
    return [
        'jan', 'feb', 'mar',
        'apr', 'may', 'jun',
        'jul', 'aug', 'sep',
        'oct', 'nov', 'dec'
    ][month - 1]
