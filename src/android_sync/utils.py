from __future__ import annotations

import datetime
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from typing import Optional


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

    @staticmethod
    def current() -> Month:
        today = datetime.date.today()
        return Month(today.year, today.month)


def get_month_name(month: int) -> str:
    assert 1 <= month <= 12
    return [
        'jan', 'feb', 'mar',
        'apr', 'may', 'jun',
        'jul', 'aug', 'sep',
        'oct', 'nov', 'dec'
    ][month - 1]


def get_month(file_name: Path) -> Optional[Month]:
    # In all cases I encountered the date was the first block of 8 digit in the file name: YYYYMMDD.
    match = re.match(r'.*?(\d{8}).*', file_name.name)
    if not match:
        return None
    date = match.group(1)
    return Month(year=int(date[:4]), month=int(date[4:6]))
