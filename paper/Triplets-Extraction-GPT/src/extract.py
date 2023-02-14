"""extract examples of tweets and triplets examples are on ucloud in
data/triplet-extraction-gpt/tagged/"""

from copy import deepcopy, copy
import random
from typing import List, Tuple, Optional
from utils import find_tweet_in_list_of_dicts


def extract_examples(
    examples: List[dict], n: int, prev_target_tweets: Optional[List[str]] = None
) -> Tuple[List[Tuple], List[str]]:
    """Extract n examples which fulfill the criteria:

        - An example with multiple triplets
        - An example w. no triplets
        - One mention
        - A multi-word verb relation
        - A single-word verb relation
        - A multi-word subj2
        - A mulit-word subj1

    Extract by randomly sampling a criteria and the randomly sampling an example from
    the examples which fulfill the criteria.

    Args:
        examples: A list of examples
        n: The number of examples to extract

    Returns:
        Tuple containing a list of tuples on the form (tweet, triplets) for examples and a list of tweets

    Example:
        >>> examples = [
        ...     {"tweet": "tweet1", "triplets": [["subj1", "verb", "subj2"]], ...},
        ...     {"tweet": "tweet2", "triplets": [], ...}
        ...     ...
        ... ]
        >>> extract_examples(examples, 9)
    """
    # create deep copy of examples
    examples_ = deepcopy(examples)

    criteria_keys = [
        "has_multiple_triplets",
        "has_no_triplets",
        "has_one_mention",
        "has_multi_word_verb",
        "has_single_word_verb",
        "has_multi_word_subj1",
        "has_multi_word_subj2",
    ]

    result = []
    if prev_target_tweets:
        for tweet in prev_target_tweets:
            tweet_dict = find_tweet_in_list_of_dicts(tweet, examples_, "resolved")

            # Remove criteria keys that in the previous target tweets which are now forced example tweets
            for criteria_key in copy(criteria_keys):
                if tweet_dict[criteria_key]:
                    criteria_keys.remove(criteria_key)

            examples_.remove(tweet_dict)
            result.append((tweet_dict["resolved"], tweet_dict["triplets"]))

    while len(result) < n:
        if criteria_keys:
            criteria_key = random.choice(criteria_keys)
            criteria_keys.remove(criteria_key)

            # examples which fulfill the criteria
            examples_fulfilling_criteria = list(
                filter(lambda x: x[criteria_key], examples_),
            )
            example = random.choice(examples_fulfilling_criteria)

            # check if example fullfills multiple criteria
            # and if so remove those from the criteria_keys
            for criteria_key in copy(criteria_keys):
                if example[criteria_key]:
                    criteria_keys.remove(criteria_key)
        else:
            example = random.choice(examples_)

        # remove example from examples_
        examples_.remove(example)
        result.append((example["resolved"], example["triplets"]))

    assert len(criteria_keys) == 0, "Not all criteria were fulfilled"

    target_tweets = [item["resolved"] for item in examples_]
    return result, target_tweets
