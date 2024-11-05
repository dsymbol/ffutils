import os
import shutil
import sys
import tempfile
from functools import partial
from pathlib import Path
from typing import Union
from urllib.parse import urlparse
from urllib.request import urlopen

from platformdirs import user_data_dir
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

install_dir = Path(user_data_dir("ffutils"))
os.environ["PATH"] += os.pathsep + str(install_dir)


class BinaryDescriptor:
    def __init__(self, exe: str):
        self.exe = exe
        self.os = sys.platform
        self.path = self.set_path()
        self.url = self.set_url()

    def set_path(self):
        if self.os == "win32":
            path = f"{self.exe}.exe"
        else:
            path = self.exe
        return install_dir / path

    def set_url(self):
        base_url = "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg"
        if self.os == "linux":
            end = "linux64-v4.1"
        elif self.os == "darwin":
            end = "osx64-v4.1"
        elif self.os == "win32":
            end = "win64-v4.1.exe"
        return f"{base_url}/{self.exe}-{end}"


def get_ffmpeg_exe() -> str:
    """
    Download the ffmpeg executable if not found.

    Returns:
        str: The absolute path to the ffmpeg executable.
    """
    bd = BinaryDescriptor("ffmpeg")

    if path := shutil.which(bd.exe):
        return path

    install_dir.mkdir(parents=True, exist_ok=True)

    download(bd.url, bd.path)
    if bd.os != "win32":
        os.chmod(bd.path, 0o755)

    return str(bd.path)


def get_ffprobe_exe() -> str:
    """
    Download the ffprobe executable if not found.

    Returns:
        str: The absolute path to the ffprobe executable.
    """
    bd = BinaryDescriptor("ffprobe")

    if path := shutil.which(bd.exe):
        return path

    install_dir.mkdir(parents=True, exist_ok=True)

    download(bd.url, bd.path)
    if bd.os != "win32":
        os.chmod(bd.path, 0o755)

    return str(bd.path)


def download(url: str, path: Union[str, os.PathLike] = None) -> None:
    if not path:
        path = urlparse(url).path.split("/")[-1]

    progress = Progress(
        TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        "•",
        DownloadColumn(),
        "•",
        TransferSpeedColumn(),
        "•",
        TimeRemainingColumn(),
    )

    with progress:
        task_id = progress.add_task(
            "download", filename=os.path.basename(path), start=False
        )
        response = urlopen(url)
        progress.update(task_id, total=int(response.info().get("Content-length")))

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                progress.start_task(task_id)
                for data in iter(partial(response.read, 32768), b""):
                    temp_file.write(data)
                    progress.update(task_id, advance=len(data))
            shutil.move(temp_file.name, path)
        except Exception as e:
            os.unlink(temp_file.name)
            raise
