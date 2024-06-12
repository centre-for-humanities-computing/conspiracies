import glob
import logging
from pathlib import Path
from typing import Union


def iter_lines_of_files(glob_pattern: Union[str, Path]):
    if isinstance(glob_pattern, Path):
        glob_pattern = glob_pattern.as_posix()
    files = glob.glob(glob_pattern, recursive=True)
    logging.debug(
        "The glob pattern '%s' resulted in the following files: %s",
        glob_pattern,
        files,
    )
    for file in files:
        with open(file) as f:
            for line in f:
                if line.strip():
                    yield line
