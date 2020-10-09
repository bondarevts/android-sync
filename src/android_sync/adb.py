import subprocess
from pathlib import Path
from typing import Any
from typing import List

from .exceptions import NoDeviceException
from .exceptions import UnauthorizedException
from .settings import ADB_PATH
from .utils import FileRecord


def _escape_spaces(value: Any) -> str:
    return str(value).replace(' ', r'\ ')


def _process_error_message(stderr: bytes):
    error_message = stderr.decode()
    if error_message.startswith('error: no devices/emulators found'):
        raise NoDeviceException(error_message)
    elif error_message.startswith('error: device unauthorized'):
        raise UnauthorizedException(error_message)
    else:
        raise Exception(error_message)


def _run_adb(*arguments: Any, verbose=False) -> bytes:
    command = [ADB_PATH.expanduser(), *arguments]
    if verbose:
        print(command)

    shell_result = subprocess.run(command, capture_output=True)
    if shell_result.stderr == b'':
        if verbose:
            print(shell_result.stdout.decode())
        return shell_result.stdout

    _process_error_message(shell_result.stderr)


def _run_adb_shell(*arguments: Any, verbose=False) -> bytes:
    shell_arguments = ' '.join([
        _escape_spaces(str(arg))
        for arg in arguments
    ])
    return _run_adb('shell', shell_arguments, verbose=verbose)


def pull(source_file: Path, target_path: Path) -> None:
    _run_adb('pull', '-a', source_file.as_posix(), target_path, verbose=True)


def list_dir(path: Path) -> List[FileRecord]:
    output = _run_adb_shell('ls', '-p', path, verbose=True)
    if not output:
        return []
    return [
        FileRecord(f'{path}/{file_name}')
        for file_name in output.decode().strip().split('\n')
    ]


def remove(path: Path) -> None:
    _run_adb_shell('rm', path, verbose=True)
    notify_file_removal(path)


def notify_file_removal(path: Path) -> None:
    _run_adb_shell(
        'am', 'broadcast',
        '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE',
        '-d', f'file://{path}',
        verbose=True
    )
