import os
import shutil
import sys
from pathlib import Path

from platformdirs import user_data_dir

from .download import download

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
