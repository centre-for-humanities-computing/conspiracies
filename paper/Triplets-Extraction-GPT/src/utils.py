import os
from typing import List


def find_tweet_in_list_of_dicts(
    tweet: str, dict_list: List[dict], key: str = "tweet"
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
            "/work", "conspiracies", "data", "triplet-extraction-gpt"
        )
        prediction_path = os.path.join(root_path, "predictions")
        with open(os.path.join("/work", "conspiracies", "openai_API_key.txt")) as f:
            openai_key = f.read()

    else:
        root_path = os.getcwd()
        openai_key = "key"
        prediction_path = root_path
        print(
            f'Invalid machine, using current path ({root_path}) and the openai key "{openai_key}"'
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


def write_triplets(triplets: List[List[str]], file: str):
    for triplet in triplets:
        if len(triplet) < 3:
            triplet = triplet + [" " for _ in range(3 - len(triplet))]
        triplet_string = f"|{triplet[0]}|{triplet[1]}|{triplet[2]}|\n"
        with open(file, "a") as f:
            f.write(triplet_string)
