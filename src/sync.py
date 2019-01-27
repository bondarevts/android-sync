import re
from pathlib import Path
from typing import List
from typing import Optional

from android_sync import adb
from android_sync.utils import FileRecord
from android_sync.utils import Month
from android_sync.utils import get_month_name
from settings import CAMERA_STORAGE_PATH
from settings import TARGET_PATH


def record_month_filter(file_name: FileRecord, month: Month) -> bool:
    prefixes = [
        'VID_',
        'Burst_Cover_GIF_Action_',
        'IMG_',
    ]
    return file_name.path.name.startswith(tuple(prefix + f'{month.year}{month.month:02}' for prefix in prefixes))


def get_month_target_folder(month: Month) -> Path:
    return Path(TARGET_PATH) / str(month.year) / f'{month.month}-{get_month_name(month.month)}'


def sync_folder(source: Path, target: Path, record_filter=None):
    target.mkdir(exist_ok=True, parents=True)
    directories_to_sync: List[FileRecord] = []
    for file in adb.list_dir(source):
        if record_filter is not None and not record_filter(file):
            continue
        if file.is_directory:
            directories_to_sync.append(file)
        else:
            adb.pull(file.path, target)

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
    months = (get_month(file.path) for file in adb.list_dir(CAMERA_STORAGE_PATH))
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
