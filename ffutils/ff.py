import os
import platform
import re
import shutil
import stat
import subprocess as sp
import sys
from tempfile import NamedTemporaryFile

import requests
from tqdm import tqdm

from pathlib import Path

BIN_PATH = Path(__file__).parent / "bin"
BIN_PATH.mkdir(parents=True, exist_ok=True)
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
    exes = [exe for exe in ["ffmpeg", "ffprobe"] if local_vars[exe]]
    os_ = platform.system()

    for exe in exes:
        if shutil.which(exe):
            continue
        url = (
                "https://github.com/imageio/imageio-binaries/raw/master/ffmpeg/"
                + BINARIES[os_][exe]
        )
        filename = BIN_PATH / f"{exe}.exe" if os_ == "Windows" else exe
        print(
            f"{exe} was not found! downloading from imageio/imageio-binaries repository."
        )
        temp = _download_exe(url, filename)
        shutil.move(temp, filename)
        os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)


def ffprog(command: list, desc: str = None, cwd: str = None) -> None:
    """
    Execute a ffmpeg command with progress.

    Args:
        command (list): The command to execute.
        desc (str, optional): Description for the progress bar. Defaults to None.
        cwd (str, optional): Changes the working directory to cwd before executing. Defaults to None.

    Raises:
        TypeError: If the `command` argument is not of type list.
        RuntimeError: If an error occurs while running the command.

    Adapted from Martin Larralde's code https://github.com/althonos/ffpb
    Personalized for my (dsymbol) use.
    """
    if not isinstance(command, list):
        raise TypeError("Command must be of type list")

    if command[0] != "ffmpeg":
        command.insert(0, "ffmpeg")
    if '-y' not in command:
        command.append('-y')

    duration_exp = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
    progress_exp = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    output = []

    with sp.Popen(
            command, stdout=sp.PIPE, stderr=sp.STDOUT, universal_newlines=True, text=True, cwd=cwd
    ) as p:
        with tqdm(total=None, desc=desc, leave=True) as t:
            for line in p.stdout:
                output.append(line)
                if duration_exp.search(line):
                    duration = duration_exp.search(line).groups()
                    t.total = (
                            int(duration[0]) * 3600
                            + int(duration[1]) * 60
                            + int(duration[2])
                    )
                elif progress_exp.search(line):
                    progress = progress_exp.search(line).groups()
                    t.update(
                        int(progress[0]) * 3600
                        + int(progress[1]) * 60
                        + int(progress[2])
                        - t.n
                    )

    if p.returncode != 0:
        message = "\n".join(
            [
                f"Error running command.",
                f"Command: {p.args}",
                f"Return code: {p.returncode}",
                f'Output: {"".join(output)}',
            ]
        )
        raise RuntimeError(message)


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
