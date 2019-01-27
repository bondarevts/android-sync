from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Iterable

from settings import ADB_PATH
from settings import CAMERA_STORAGE_PATH
from settings import TARGET_PATH


def get_month_name(month: int) -> str:
    return {
        1: 'jan',
        2: 'feb',
        3: 'mar',
        4: 'apr',
        5: 'may',
        6: 'jun',
        7: 'jul',
        8: 'aug',
        9: 'sep',
        10: 'oct',
        11: 'nov',
        12: 'dec',
    }[month]


@dataclass
class FileRecord:
    path: Path
    is_directory: bool


@dataclass(order=True)
class Month:
    year: int
    month: int

    @staticmethod
    def segment(start: Month, end: Month) -> Iterable[Month]:
        year = start.year

        if start.year == end.year:
            yield from (Month(year, month) for month in range(start.month, end.month + 1))
            return

        for month in range(start.month, 13):
            yield Month(year, month)

        year += 1
        while year != end.year:
            yield from (Month(year, month) for month in range(1, 13))
            year += 1

        yield from (Month(year, month) for month in range(1, end.month + 1))


def record_month_filter(file_name: FileRecord, month: Month) -> bool:
    prefixes = [
        'VID_',
        'Burst_Cover_GIF_Action_',
        'IMG_',
    ]
    return file_name.path.name.startswith(tuple(prefix + f'{month.year}{month.month:02}' for prefix in prefixes))


def get_month_target_folder(month: Month) -> Path:
    return Path(TARGET_PATH) / str(month.year) / f'{month.month}-{get_month_name(month.month)}'


def pull(source_file: Path, target_path: Path) -> None:
    os.system(f"{ADB_PATH} pull -a '{source_file}' '{target_path}'")


def list_dir(path: Path) -> List[FileRecord]:
    def is_directory(file_name: str) -> bool:
        return file_name[-1] == '/'
    escaped_path = path.name.replace(' ', r'\ ')
    print(f"{ADB_PATH} shell 'ls -p {escaped_path}")
    shell_result = subprocess.run(f"{ADB_PATH} shell 'ls -p {escaped_path}'", shell=True, capture_output=True)
    output: bytes = shell_result.stdout
    if not output:
        return []
    return [
        FileRecord(Path(path) / file_name, is_directory(file_name))
        for file_name in output.decode().strip().split('\n')
    ]


def sync_folder(source: Path, target: Path, record_filter=None):
    target.mkdir(exist_ok=True, parents=True)
    directories_to_sync: List[FileRecord] = []
    for file in list_dir(source):
        if record_filter is not None and not record_filter(file):
            continue
        if file.is_directory:
            directories_to_sync.append(file)
        else:
            pull(file.path, target)

    for directory in directories_to_sync:
        sync_folder(directory.path, target / directory.path.name)


def sync_all() -> None:
    target_path = Path(TARGET_PATH) / 'all'
    sync_folder(CAMERA_STORAGE_PATH, target_path)


def sync_month_prompt() -> None:
    period = input("Sync period [year month]:")
    month = Month(*map(int, period.split()))
    sync_month(month)


def sync_month(month: Month) -> None:
    sync_folder(CAMERA_STORAGE_PATH, get_month_target_folder(month),
                lambda file_name: record_month_filter(file_name, month))


def get_month(file_name: Path) -> Optional[Month]:
    match = re.match(r'.*?(\d{8}).*', file_name.name)
    if not match:
        return None
    date = match.group(1)
    return Month(int(date[:4]), int(date[4:6]))


def sync_by_month() -> None:
    months = (get_month(file.path) for file in list_dir(CAMERA_STORAGE_PATH))
    months = [month for month in months if month]
    start_month = min(months)
    end_month = max(months)
    for month in Month.segment(start_month, end_month):
        sync_month(month)


def sync_folder_prompt():
    source = Path(input('From: '))
    target = Path(input('To: ')).expanduser()
    sync_folder(source, target)


def main() -> None:
    sync_folder_prompt()


if __name__ == "__main__":
    main()
