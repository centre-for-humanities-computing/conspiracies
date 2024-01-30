import glob
import logging


def iter_lines_of_files(glob_pattern: str):
    files = glob.glob(glob_pattern, recursive=True)
    logging.debug(
        "The glob pattern '%s' resulted in the following files: %s",
        glob_pattern,
        files,
    )
    for file in files:
        with open(file) as f:
            for line in f:
                yield line
