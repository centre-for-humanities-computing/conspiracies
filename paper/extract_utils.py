import ndjson
from typing import List, Union, Tuple
from glob import glob


def load_ndjson(path: str) -> List[dict]:
    """Loads ndjson file
    Args:
        path (str): path to ndjson file
    Returns:
        data (dict): data from ndjson file
    """
    with open(path, "r") as f:
        data = ndjson.load(f)
    return data


def ndjson_gen(filepath: str):
    """Creates a generator for ndjson files and yields the tweets."""
    for file in glob(filepath):
        with open(file) as f:
            reader = ndjson.reader(f)
            for post in reader:
                yield post


def write_txt(
    path: str,
    data: Union[List[str], List[Tuple[str, str, str]]],
    method="a",
):
    """Writes data to txt file. Can take either a list of strings or a list of tuples.
    List of strings is e.g. list of subjects, predicates, or objects.
    List of tuples is e.g. list of triplets.
    Args:
        path (str): path to txt file
        data (Union[List[str], List[tuple]]): data to write to file
        method (str, optional): method to use when writing data. Defaults to "a" (i.e., append).

    Returns:
        None
    """
    with open(path, method) as f:
        if isinstance(data[0], tuple):
            f.write("\n".join([", ".join(triplet) for triplet in data]))
        elif isinstance(data[0], str):
            f.write("\n".join(data))  # type: ignore
        f.write("\n")
