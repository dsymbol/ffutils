import os
import shutil
import tempfile
from typing import Union
from urllib.parse import urlparse

import requests
from rich.progress import (
    BarColumn,
    DownloadColumn,
    FileSizeColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)


def download(url: str, path: Union[str, os.PathLike] = None) -> None:
    if not path:
        path = os.path.basename(urlparse(url).path)

    response = requests.get(url, stream=True)
    response.raise_for_status()
    size = response.headers.get("content-length")

    if size:
        total_size = int(size)
        columns = (
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )
    else:
        total_size = None
        columns = (
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            FileSizeColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeElapsedColumn(),
        )

    with Progress(*columns) as progress:
        task_id = progress.add_task(
            f"[bold blue]{os.path.basename(path)}",
            start=False,
            total=total_size,
        )

        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                progress.start_task(task_id)
                for data in response.iter_content(8192):
                    temp_file.write(data)
                    progress.update(task_id, advance=len(data))
            shutil.move(temp_file.name, path)
        except Exception as e:
            os.unlink(temp_file.name)
            raise e
