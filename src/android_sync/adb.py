import os
import subprocess
from pathlib import Path
from typing import List

from android_sync.utils import FileRecord
from settings import ADB_PATH


def _escape_path(path: Path) -> str:
    return str(path).replace(' ', r'\ ')


def pull(source_file: Path, target_path: Path) -> None:
    os.system(f"{ADB_PATH} pull -a '{source_file}' '{target_path}'")


def list_dir(path: Path) -> List[FileRecord]:
    def is_directory(file_name: str) -> bool:
        return file_name[-1] == '/'

    escaped_path = _escape_path(path)
    shell_result = subprocess.run(f"{ADB_PATH} shell 'ls -p {escaped_path}'", shell=True, capture_output=True)
    output: bytes = shell_result.stdout
    if not output:
        return []
    return [
        FileRecord(Path(path) / file_name, is_directory(file_name))
        for file_name in output.decode().strip().split('\n')
    ]


def remove(path: Path) -> None:
    print(f"{ADB_PATH} shell 'rm {_escape_path(path)}'")
    os.system(f"{ADB_PATH} shell 'rm {_escape_path(path)}'")
    notify_file_removal(path)


def notify_file_removal(path: Path) -> None:
    os.system(f"{ADB_PATH} shell 'am broadcast "
              f"-a android.intent.action.MEDIA_SCANNER_SCAN_FILE "
              f"-d file://{_escape_path(path)}'")
