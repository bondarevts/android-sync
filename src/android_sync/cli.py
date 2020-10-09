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

    month_command = subparsers.add_parser('month')
    month_command.add_argument('--move', action='store_true')
    month_command.add_argument('month', help='YYYY-MM', action='store', nargs='?')

    folder_command = subparsers.add_parser('folder')
    folder_command.add_argument('device_path')
    folder_command.add_argument('target_path')
    return parser.parse_args()


def parse_month(value: str) -> Month:
    year, month = value.split('-')
    return Month(year=int(year), month=int(month))


def should_retry(answer):
    return not answer.lower().startswith('n')


def main() -> None:
    args = parse_args()
    if args.command == 'all':
        raise Exception('Not implemented yet')

    if args.command == 'month':
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

    if args.command == 'folder':
        sync_folder(args.device_path, args.target_path)


if __name__ == '__main__':
    main()
