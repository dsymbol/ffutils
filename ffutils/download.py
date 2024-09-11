import os
import shutil
import stat
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Union

import requests
from tqdm import tqdm

URL = "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/"
BINARIES = {
    "linux": {"ffmpeg": "ffmpeg-linux64-v4.1", "ffprobe": "ffprobe-linux64-v4.1"},
    "darwin": {"ffmpeg": "ffmpeg-osx64-v4.1", "ffprobe": "ffprobe-osx64-v4.1"},
    "win32": {"ffmpeg": "ffmpeg-win64-v4.1.exe", "ffprobe": "ffprobe-win64-v4.1.exe"},
}

bin_ = Path(__file__).parent / "bin"
os_ = sys.platform
bin_.mkdir(parents=True, exist_ok=True)
os.environ["PATH"] += os.pathsep + str(bin_)


def get_ffmpeg_exe() -> str:
    """
    Download the ffmpeg executable if not found.

    Returns:
        str: The absolute path to the ffmpeg executable.
    """
    exe = "ffmpeg"

    if path := shutil.which(exe):
        return path

    url = URL + BINARIES[os_][exe]
    filename = bin_ / f"{exe}.exe" if os_ == "win32" else exe
    _download_exe(url, filename)
    os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)
    return str(filename)


def get_ffprobe_exe() -> str:
    """
    Download the ffprobe executable if not found.

    Returns:
        str: The absolute path to the ffprobe executable.
    """
    exe = "ffprobe"

    if path := shutil.which(exe):
        return path

    url = URL + BINARIES[os_][exe]
    filename = bin_ / f"{exe}.exe" if os_ == "win32" else exe
    _download_exe(url, filename)
    os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)
    return str(filename)



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
