import argparse

from android_sync.exceptions import NoDeviceException
from android_sync.exceptions import UnauthorizedException
from android_sync.sync import sync_folder
from android_sync.sync import sync_month
from android_sync.utils import Month


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser('async')
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('all')

    month_parser = subparsers.add_parser('month')
    month_parser.add_argument('--move', action='store_true')
    month_parser.add_argument('month', help='YYYY-MM', action='store', nargs='?')

    folder_parser = subparsers.add_parser('folder')
    folder_parser.add_argument('device_path')
    folder_parser.add_argument('target_path')
    return parser.parse_args()


def parse_month(value: str) -> Month:
    year, month = value.split('-')
    return Month(year=int(year), month=int(month))


def should_retry(answer):
    return not answer.lower().startswith('n')


def folder_command(args):
    sync_folder(args.device_path, args.target_path)


def month_command(args):
    if args.month is None:
        month = Month.current()
    else:
        month = parse_month(args.month)

    answer = ''
    while should_retry(answer):
        try:
            sync_month(month, clean=args.move)
        except NoDeviceException:
            answer = input('Device is not found. Please plug in the device.\nRetry [Y/n]? ')
        except UnauthorizedException:
            answer = input('Connection is not authorized. Please check the dialog on the device screen. '
                           'Retry [Y/n]? ')
        else:
            answer = 'no'


def main() -> None:
    args = parse_args()
    if args.command == 'all':
        raise Exception('Not implemented yet')

    if args.command == 'month':
        month_command(args)

    if args.command == 'folder':
        folder_command(args)


if __name__ == '__main__':
    main()
