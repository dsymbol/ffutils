import re
import shlex
import subprocess as sp
from typing import Union

from rich.progress import Progress


def ffprog(command: Union[list, str], desc: str = "Processing...", cwd: str = None) -> None:
    """
    Execute a ffmpeg command with progress.

    Args:
        command (list, str): The command to execute.
        desc (str, optional): Description for the progress bar. Defaults to None.
        cwd (str, optional): Changes the working directory to cwd before executing. Defaults to None.

    Raises:
        RuntimeError: If an error occurs while running the command.
    """
    command = command if isinstance(command, list) else shlex.split(command)

    if command[0] != "ffmpeg":
        command.insert(0, "ffmpeg")
    if "-y" not in command:
        command.append("-y")

    duration_exp = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2})\.\d{2}")
    progress_exp = re.compile(r"time=(\d{2}):(\d{2}):(\d{2})\.\d{2}")
    output = []

    with sp.Popen(
        command,
        stdout=sp.PIPE,
        stderr=sp.STDOUT,
        universal_newlines=True,
        text=True,
        cwd=cwd,
    ) as p, Progress() as progress:
        task = progress.add_task(f'[green]{desc}', total=None)
        for line in p.stdout:
            output.append(line)
            if duration_exp.search(line):
                total_duration = duration_exp.search(line).groups()
                progress.update(
                    task,
                    total=(
                        int(total_duration[0]) * 3600
                        + int(total_duration[1]) * 60
                        + int(total_duration[2])
                    ),
                )
            elif progress_exp.search(line):
                current_progress = progress_exp.search(line).groups()
                progress.update(
                    task,
                    completed=(
                        int(current_progress[0]) * 3600
                        + int(current_progress[1]) * 60
                        + int(current_progress[2])
                    ),
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
