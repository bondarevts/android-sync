from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# There is no way to distinguish a Path to a directory from a Path to a file.
# To avoid making a separate call on the phone, we can store this information.
@dataclass
class FileRecord:
    path: Path
    is_directory: bool

    def __init__(self, file_name: str):
        self.path = Path(file_name)
        self.is_directory = self._is_directory(file_name)

    @staticmethod
    def _is_directory(file_name: str) -> bool:
        return file_name[-1] == '/'


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
