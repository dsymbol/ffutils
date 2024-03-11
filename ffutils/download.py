import os
import platform
import shutil
import stat
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from tqdm import tqdm

BIN_PATH = Path(__file__).parent / "bin"
os.environ["PATH"] += os.pathsep + str(BIN_PATH)

BINARIES = {
    "Linux": {"ffmpeg": "ffmpeg-linux64-v4.1", "ffprobe": "ffprobe-linux64-v4.1"},
    "Darwin": {"ffmpeg": "ffmpeg-osx64-v4.1", "ffprobe": "ffprobe-osx64-v4.1"},
    "Windows": {"ffmpeg": "ffmpeg-win64-v4.1.exe", "ffprobe": "ffprobe-win64-v4.1.exe"},
}


def get_ffmpeg_exe(ffmpeg: bool = True, ffprobe: bool = False) -> None:
    """
    Download the ffmpeg executable if not found in PATH.

    Args:
        ffmpeg (bool, optional): Whether to download ffmpeg. Defaults to True.
        ffprobe (bool, optional): Whether to download ffprobe. Defaults to False.
    """
    local_vars = locals().copy()
    exes = [exe for exe in ["ffmpeg", "ffprobe"] if local_vars[exe] and not shutil.which(exe)]

    if not exes:
        return

    BIN_PATH.mkdir(parents=True, exist_ok=True)
    os_ = platform.system()

    for exe in exes:
        url = f"https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/{BINARIES[os_][exe]}"
        filename = BIN_PATH / f"{exe}.exe" if os_ == "Windows" else exe
        print(f"{exe} was not found! downloading from imageio/imageio-binaries repository.")
        temp = _download_exe(url, filename)
        shutil.move(temp, filename)
        os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)


def _download_exe(url: str, filename: str | Path) -> str:
    r = requests.get(url, stream=True)
    file_size = int(r.headers.get("content-length", 0))
    chunk_size = 1024

    try:
        with NamedTemporaryFile(mode="wb", delete=False) as temp, tqdm(
                desc=filename.name,
                total=file_size,
                ncols=80,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
                leave=True,
        ) as bar:
            for chunk in r.iter_content(chunk_size=chunk_size):
                size = temp.write(chunk)
                bar.update(size)
    except Exception as f:
        os.remove(temp.name)
        sys.exit(str(f))

    return temp.name
