import argparse
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('async')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('all')

    month_command = subparsers.add_parser('month')
    month_command.add_argument('--month', help='YYYY-MM')

    move_command = subparsers.add_parser('move')
    move_command.add_argument('month', help='YYYY-MM')

    folder_command = subparsers.add_parser('folder')
    folder_command.add_argument('device_path')
    folder_command.add_argument('target_path')
    return parser.parse_args()


def parse_month(value: str) -> Month:
    year, month = value.split('-')
    return Month(year=int(year), month=int(month))


def main() -> None:
    args = parse_args()
    if args.command == 'all':
        raise Exception('Not implemented yet')

    if args.command == 'month':
        if args.month is None:
            month = Month.current()
        else:
            month = parse_month(args.month)
        sync_month(month)
        return

    if args.command == 'move':
        sync_month(parse_month(args.month), clean=True)
        return

    if args.command == 'folder':
        sync_folder(args.device_path, args.target_path)


if __name__ == '__main__':
    main()
