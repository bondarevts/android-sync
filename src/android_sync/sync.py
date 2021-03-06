from pathlib import Path
from typing import Callable

from android_sync import adb
from android_sync.settings import DEVICE_STORAGE_PATH
from android_sync.settings import TARGET_PATH
from android_sync.utils import FileRecord
from android_sync.utils import Month
from android_sync.utils import get_month
from android_sync.utils import get_month_name


def belongs_to_month(file_record: FileRecord, month: Month) -> bool:
    accepted_prefixes = tuple(f'{prefix}{month.year}{month.month:02}' for prefix in (
        'VID_',
        'Burst_Cover_GIF_Action_',
        'IMG_',
        'PANO_'
    ))
    return file_record.path.name.startswith(accepted_prefixes)


def get_month_target_folder(month: Month) -> Path:
    return Path(TARGET_PATH).expanduser() / str(month.year) / f'{month.month}-{get_month_name(month.month)}'


def sync_folder(
        device_path: Path,
        target_path: Path,
        is_accepted_file_record: Callable[[FileRecord], bool] = None,
        *, clean: bool = False):
    target_path.mkdir(exist_ok=True, parents=True)

    for file in adb.list_dir(device_path):
        if is_accepted_file_record is not None and not is_accepted_file_record(file):
            continue
        if file.is_directory:
            sync_folder(file.path, target_path / file.path.name)
            continue

        if (target_path / file.path.name).exists():
            print(f'Skipped: {file.path.name}')
        else:
            adb.pull(file.path, target_path)
        if clean:
            adb.remove(file.path)


def sync_all() -> None:
    target_path = TARGET_PATH.expanduser() / 'all'
    sync_folder(DEVICE_STORAGE_PATH, target_path)


def sync_month(month: Month, *, clean: bool = False) -> None:
    sync_folder(DEVICE_STORAGE_PATH, get_month_target_folder(month),
                lambda file_record: belongs_to_month(file_record, month),
                clean=clean)


def sync_by_month() -> None:
    months = (get_month(file.path) for file in adb.list_dir(DEVICE_STORAGE_PATH))
    months = [month for month in months if month]
    for month in Month.segment(start=min(months), end=max(months)):
        sync_month(month)


def clean_folder(device_path: Path) -> None:
    for file in adb.list_dir(device_path):
        if file.is_directory:
            continue
        adb.remove(file.path)
