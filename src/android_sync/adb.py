import contextlib
import io
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from typing import List
from typing import Optional

from .exceptions import NoDeviceException
from .exceptions import UnauthorizedException
from .settings import ADB_PATH
from .utils import FileRecord

_PROGRESS_BLOCK_PATTERN = re.compile(r'\[ *\d+%]')


def _escape_spaces(value: Any) -> str:
    return str(value).replace(' ', r'\ ')


def _process_error_message(error_message: str) -> None:
    if error_message.startswith('error: no devices/emulators found'):
        raise NoDeviceException(error_message)
    elif error_message.startswith('error: device unauthorized'):
        raise UnauthorizedException(error_message)
    else:
        raise Exception(error_message)


def _run_command(command: List[str], *, verbose: bool = False) -> Optional[str]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, errors='replace')
    stream = sys.stdout if verbose else io.StringIO()
    with contextlib.redirect_stdout(stream):
        _merge_progress_block(process.stdout)
    process.wait()
    _process_error_message(process.stderr.read())
    return None if verbose else stream.getvalue()


def _merge_progress_block(stream):
    """ Merges lines like
    [  0%] Text
    [  1%] Text2

    into one line:
    [  1%] Text2

    Everything else is passed through unchanged.
    """

    is_progress_block = False
    cleanup_width = 1  # 0 doesn't work with format line, 1 will not affect anything
    for line in iter(stream.readline, ''):
        line = line.rstrip('\n')
        if _PROGRESS_BLOCK_PATTERN.match(line):
            if not is_progress_block:
                print('\n', end='')
                is_progress_block = True
            else:
                print('\r', end='')
            print(f'{line:{cleanup_width}}', end='')  # override the previous line with spaces
            cleanup_width = len(line)
        else:
            if is_progress_block:
                is_progress_block = False
                print()
            print(line)


def _run_adb(*arguments: Any, verbose=False) -> str:
    command = [ADB_PATH.expanduser(), *arguments]
    if verbose:
        print(command)

    return _run_command(command, verbose=verbose)


def _run_adb_shell(*arguments: Any, verbose=False) -> str:
    shell_arguments = ' '.join([
        _escape_spaces(str(arg))
        for arg in arguments
    ])
    return _run_adb('shell', shell_arguments, verbose=verbose)


def pull(source_file: Path, target_path: Path) -> None:
    _run_adb('pull', '-a', source_file.as_posix(), target_path, verbose=True)


def list_dir(path: Path) -> List[FileRecord]:
    output = _run_adb_shell('ls', '-p', path)
    if not output:
        return []
    return [
        FileRecord(f'{path}/{file_name}')
        for file_name in output.strip().split('\n')
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
