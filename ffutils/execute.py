import re
import subprocess as sp

from tqdm import tqdm


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
