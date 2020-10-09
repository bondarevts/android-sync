import os
import subprocess
from pathlib import Path
from typing import List

from .settings import ADB_PATH
from .utils import FileRecord


def _escape_path(path: Path) -> str:
    return str(path).replace(' ', r'\ ')


def pull(source_file: Path, target_path: Path) -> None:
    os.system(f"{ADB_PATH} pull -a '{source_file}' '{target_path}'")


def list_dir(path: Path) -> List[FileRecord]:
    escaped_path = _escape_path(path)
    shell_result = subprocess.run(f"{ADB_PATH} shell 'ls -p {escaped_path}'", shell=True, capture_output=True)
    if shell_result.stderr != b'':
        print(f'ERROR: "{shell_result.stderr.decode()}"')
    output: bytes = shell_result.stdout
    if not output:
        return []
    return [
        FileRecord(f'{path}/{file_name}')
        for file_name in output.decode().strip().split('\n')
    ]


def remove(path: Path) -> None:
    command = f"{ADB_PATH} shell 'rm {_escape_path(path)}'"
    print(command)
    os.system(command)
    notify_file_removal(path)


def notify_file_removal(path: Path) -> None:
    os.system(f"{ADB_PATH} shell 'am broadcast "
              f"-a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
              f"-d file://{_escape_path(path)}'")
