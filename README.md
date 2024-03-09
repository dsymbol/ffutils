# ffutils

Utilities for working with ffmpeg, such as downloading ffmpeg executables and displaying progress for ffmpeg commands.

## Installation

To install the library, use pip:

```bash
pip install ffutils
```

Alternatively, install the latest directly from the GitHub repository:

```bash
pip install git+https://github.com/dsymbol/ffutils.git
```

## Usage

```python
from ffutils import get_ffmpeg_exe, ffprog

# Download ffmpeg executable if not found in PATH
get_ffmpeg_exe()

# Example ffmpeg command to convert a video with progress
command = ["ffmpeg", "-i", "input.mp4", "output.mkv"]
ffprog(command, desc="Converting video")
```

Combine [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) and a progress bar:

```python
import ffmpeg
from ffutils import get_ffmpeg_exe, ffprog

get_ffmpeg_exe()

command = (
    ffmpeg
    .input('video.mp4')
    .output('output.mkv')
).get_args()

ffprog(
    command,
    desc="Converting video"
)
```
