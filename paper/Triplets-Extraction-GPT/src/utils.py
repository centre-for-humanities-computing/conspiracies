import os
import re
from typing import List, Optional
from collections import Counter
from copy import deepcopy


def find_tweet_in_list_of_dicts(
    tweet: str,
    dict_list: List[dict],
    key: str = "tweet",
) -> dict:
    """Finds the dict in a list of dict that contains the tweet in question.

    Args:
        tweet (str): the tweet to find
        dict_list (List[dict]): list of dictionaries containing tweets and other information
        key (str, optional): the key that stores the tweets in the dicts. Usually 'tweet' or 'original_tweet'

    Returns:
        d (dict): the dictionary where tweet is in
    """
    for d in dict_list:
        if d[key] == tweet:
            return d


def get_paths(machine: str, get_openai_key: bool = False):
    """Returns appropriate path depending on machine.

    Args:
        machine (str): current machine. Specialized to 'grundtvig' or 'ucloud'
        get_openai_key (bool, optional): Whether or not to return the open ai key. Defaults to False.

    Returns:
        root_path (str): path to where data is stored
        prediction_path (str): path to where predictions should be saved
        openai_key (str, optional): the key for accessing open ai. Only returned if get_openai_key is True
    """
    if machine == "grundtvig":
        root_path = os.path.join("/data", "conspiracies", "triplet-extraction-gpt")
        prediction_path = os.path.join(
            "/home",
            os.getlogin(),
            "data",
            "predictions",
        )
        with open(os.path.join("/home", os.getlogin(), "openai_API_key.txt")) as f:
            openai_key = f.read()

    elif machine == "ucloud":
        root_path = os.path.join(
            "/work",
            "conspiracies",
            "data",
            "triplet-extraction-gpt",
        )
        prediction_path = os.path.join(root_path, "predictions")
        with open(os.path.join("/work", "conspiracies", "openai_API_key.txt")) as f:
            openai_key = f.read()

    else:
        root_path = os.getcwd()
        openai_key = "key"
        prediction_path = root_path
        print(
            f'Invalid machine, using current path ({root_path}) and the openai key "{openai_key}"',
        )

    if get_openai_key:
        return root_path, prediction_path, openai_key
    else:
        return root_path, prediction_path


def get_triplet_from_string(triplet_string: str) -> List[List[str]]:
    rows = triplet_string.split("\n")
    triplets = [
        [element for element in row.split("|") if element.strip()] for row in rows
    ]
    return triplets


def sanity_check_triplets(
    triplets: List[List[str]],
    counter: Optional[Counter] = None,
) -> List[List[str]]:
    """Sanity check for a given set of triplets. Checks if triplets indicate
    template is trying to start new table, if triplet start with a new tweet
    (not the target tweet) and if triplets are exactly three elements long. It
    removes such none-sane triplets from the list.

    Args:
        triplets (List[List[str]]): List of triplets where each triplet is a list of string
        counter (Optional[Counter], optional): counter to keep count of extraction errors. Defaults to None, in which case no count is kept.

    Returns:
        List[List[str]]: The triplet list with non-sane triplets removed
    """
    triplet_copy = deepcopy(triplets)
    stop_words = ["Subject", "Predicate", "Object", "---"]

    for triplet in triplets:
        # If any of the elements in the triplet contains a stopword
        if any(word in element for word in stop_words for element in triplet):
            triplet_copy.remove(triplet)

        # If the triplet does not contain exactly three elements
        if len(triplet) != 3:
            if counter:
                counter.update({"extraction_errors": 1})
            triplet_copy.remove(triplet)
            continue

        # If the template has guessed that another tweet would be coming
        if any(bool(re.search("@\w+:", element)) for element in triplet):
            triplet_copy.remove(triplet)
            break

    return triplet_copy


def write_triplets(
    triplets: List[List[str]],
    file: str,
    source: str,
    counter: Optional[Counter] = None,
):
    """Writes triplets to a given input file in markdown friendly print.
    Performs sanity-checks of triplets first.

    Args:
        triplets (List[List[str]]): List of triplets, where each triplet is a list of strings
        file (str): file to write triplets to
        source (str): identifier for source of triplet (gold tagging or template output)
        counter (Optional[Counter], optional): counter to keep count of extraction errors. Defaults to None, in which case no count is kept.
    """
    checked_triplets = sanity_check_triplets(triplets, counter)

    # If there are no sane triplets for the tweet add empty row
    if not checked_triplets:
        triplet_string = f"|**{source}**||||\n"
        with open(file, "a") as f:
            f.write(triplet_string)

    else:
        for i, triplet in enumerate(checked_triplets):
            # If it is the first row of printing, we also indicate sorce
            if i == 0:
                triplet_string = (
                    f"|**{source}**|{triplet[0]}|{triplet[1]}|{triplet[2]}|\n"
                )
            else:
                triplet_string = f"||{triplet[0]}|{triplet[1]}|{triplet[2]}|\n"
            with open(file, "a") as f:
                f.write(triplet_string)
