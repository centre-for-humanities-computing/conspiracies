"""extract examples of tweets and triplets examples are on ucloud in
data/triplet-extraction-gpt/tagged/"""

from copy import deepcopy, copy
import random
import re
from typing import List, Tuple, Optional
from utils import find_tweet_in_list_of_dicts
from spacy.tokens import Doc
from conspiracies.prompt_relation_extraction.data_classes import SpanTriplet


def has_multiple_triplets(spacy_triplets: SpanTriplet):
    return len(spacy_triplets) > 1


def has_no_triplets(spacy_triplets: SpanTriplet):
    return len(spacy_triplets) == 0


def has_one_mention(text_doc: Doc):
    return bool(re.search(r"@[\w]+", text_doc.text))


def has_multi_word_verb(spacy_triplets: SpanTriplet):
    for triplet in spacy_triplets:
        if len(triplet.predicate) > 1:
            return True
    else:
        return False


def has_single_word_verb(spacy_triplets: SpanTriplet):
    for triplet in spacy_triplets:
        if len(triplet.predicate) == 1:
            return True
    else:
        return False


def has_multi_word_subj(spacy_triplets: SpanTriplet):
    for triplet in spacy_triplets:
        if len(triplet.subject) > 1:
            return True
    else:
        return False


def has_multi_word_obj(spacy_triplets: SpanTriplet):
    for triplet in spacy_triplets:
        if len(triplet.object) > 1:
            return True
    else:
        return False


def extract_examples(
    examples: List[dict],
    n: int,
    prev_target_tweets: Optional[List[str]] = None,
    html_tagged: Optional[bool] = False,
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

    target_key = "html_example" if html_tagged else "triplets"

    criteria_keys = [
        "has_multiple_triplets",
        "has_no_triplets",
        "has_one_mention",
        "has_multi_word_verb",
        "has_single_word_verb",
        "has_multi_word_subj1",
        "has_multi_word_subj2",
    ]
    if html_tagged:
        examples_ = [d for d in examples_ if "html_example" in d.keys()]
        criteria_keys = []

    result = []
    if prev_target_tweets:
        for tweet in prev_target_tweets:
            tweet_dict = find_tweet_in_list_of_dicts(tweet, examples_, "resolved")

            # Remove criteria keys that in the previous target tweets which are now forced example tweets
            for criteria_key in copy(criteria_keys):
                if tweet_dict[criteria_key]:
                    criteria_keys.remove(criteria_key)

            examples_.remove(tweet_dict)
            result.append((tweet_dict["resolved"], tweet_dict[target_key]))

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
        result.append((example["resolved"], example[target_key]))

    assert len(criteria_keys) == 0, "Not all criteria were fulfilled"

    target_tweets = [item["resolved"] for item in examples_]
    return result, target_tweets


def criteria_sampling(criteria_keys, n_target, example_dicts):
    target_examples = []
    while len(target_examples) < n_target:
        try:
            criteria = random.choice(list(criteria_keys.keys()))
            subset_function = criteria_keys[criteria]
            function_key = "doc" if criteria == "has_one_mention" else "triplets"

            # Filter only examples that fulfill the criteria
            useful_examples = list(
                filter(lambda x: subset_function(x[function_key]), example_dicts),
            )

            target = random.choice(useful_examples)
            criteria_keys.pop(criteria)

        except:
            target = random.choice(example_dicts)

        target_examples.append(target)
        example_dicts.remove(target)
    return target_examples, example_dicts


def extract_spacy_examples(
    examples: List[dict],
    n_target,
    cv=1,
):
    # example_dicts = deepcopy(examples)
    example_dicts = [{"doc": d["doc"], "triplets": d["triplets"]} for d in examples]

    target_list = []
    example_list = []
    for c in range(cv):
        criteria_keys = {
            "has_multiple_triplets": has_multiple_triplets,
            "has_no_triplets": has_no_triplets,
            "has_one_mention": has_one_mention,
            "has_multi_word_verb": has_multi_word_verb,
            "has_single_word_verb": has_single_word_verb,
            "has_multi_word_subj1": has_multi_word_subj,
            "has_multi_word_obj": has_multi_word_obj,
        }
        extracted_targets, extracted_examples = criteria_sampling(
            criteria_keys, n_target, example_dicts
        )
        # print(f'extracted {len(extracted_targets)} targets and {len(extracted_examples)} examples in cv round {c+1}')
        example_list.append(
            [ex for prev_target in target_list for ex in prev_target]
            + extracted_examples
        )
        target_list.append(extracted_targets)

    return target_list, example_list
