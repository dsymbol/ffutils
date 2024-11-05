import os
import shutil
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union

import requests
from tqdm import tqdm

bin_ = Path(__file__).parent / "bin"
bin_.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] += os.pathsep + str(bin_)


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
        return bin_ / path

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

    _download_exe(bd.url, bd.path)
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

    _download_exe(bd.url, bd.path)
    if bd.os != "win32":
        os.chmod(bd.path, 0o755)

    return str(bd.path)


def _download_exe(url: str, filename: Union[str, Path]) -> None:
    r = requests.get(url, stream=True)
    r.raise_for_status()
    file_size = int(r.headers.get("content-length", 0))
    chunk_size = 1024

    try:
        with NamedTemporaryFile(mode="wb", delete=False) as temp, tqdm(
            desc=Path(filename).name,
            total=file_size,
            ncols=80,
            unit="iB",
            unit_scale=True,
            unit_divisor=chunk_size,
            leave=True,
        ) as bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                size = temp.write(chunk)
                bar.update(size)
    except Exception as f:
        os.remove(temp.name)
        sys.exit(str(f))

    shutil.move(temp.name, filename)
