"""Extract examples of tweets and triplets. Examples are on ucloud in
data/triplet-extraction-gpt/tagged/ and on Grundtvig in.

/data/conspiracies/triplet-extraction-gpt
"""

import random
import re
from typing import List, Tuple
from spacy.tokens import Doc
from conspiracies.docprocessing.relationextraction.data_classes import (
    DocTriplets,
)


def has_multiple_triplets(spacy_triplets: DocTriplets):
    return len(spacy_triplets) > 1


def has_no_triplets(spacy_triplets: DocTriplets):
    return len(spacy_triplets) == 0


def has_one_mention(text_doc: Doc):
    return bool(re.search(r"@[\w]+", text_doc.text))


def has_multi_word_verb(spacy_triplets: DocTriplets):
    for triplet in spacy_triplets:
        if len(triplet.predicate) > 1:
            return True
    else:
        return False


def has_single_word_verb(spacy_triplets: DocTriplets):
    for triplet in spacy_triplets:
        if len(triplet.predicate) == 1:
            return True
    else:
        return False


def has_multi_word_subj(spacy_triplets: DocTriplets):
    for triplet in spacy_triplets:
        if len(triplet.subject) > 1:
            return True
    else:
        return False


def has_multi_word_obj(spacy_triplets: DocTriplets):
    for triplet in spacy_triplets:
        if len(triplet.object) > 1:
            return True
    else:
        return False


def criteria_sampling(
    criteria_keys: dict,
    n_target: int,
    input_examples: List[Doc],
):
    """This function tries to extract examples that fulfill the criteria, so
    that as many of the criteria as possible are fulfilled in the target
    tweets.

    If that is not possible, it will just sample randomly.
    """
    target_examples: List[Doc] = []
    while len(target_examples) < n_target:
        try:
            criteria = random.choice(list(criteria_keys.keys()))
            subset_function = criteria_keys[criteria]
            # function_key = "doc" if criteria == "has_one_mention" else "triplets"

            # Filter only examples that fulfill the criteria
            if criteria == "has_one_mention":
                useful_examples = list(
                    filter(lambda x: subset_function(x), input_examples),
                )
            else:
                useful_examples = list(
                    filter(
                        lambda x: subset_function(x._.relation_triplets),
                        input_examples,
                    ),
                )

            target = random.choice(useful_examples)
            criteria_keys.pop(criteria)

        except IndexError:
            target = random.choice(input_examples)

        target_examples.append(target)
        input_examples.remove(target)
    return target_examples, input_examples


def extract_examples(
    examples: List[Doc],
    n_target: int,
    cv: int = 1,
) -> Tuple[List[List[Doc]], List[List[Doc]]]:
    """This function extracts examples and targets for the triplet extraction
    task. It tries to extract examples that fulfill the criteria, so that as
    many of the criteria as possible are fulfilled in the target tweets. It can
    also be used to create cross validation sets.

    Args:
        examples (List[Doc]): tagged examples to extract from
        n_target (int): number of target examples to extract
        cv (int, optional): number of cv-sets to make. Defaults to 1,
            which means only one set of targets and examples are extracted.

    Returns:
        Tuple[List[List[Doc]], List[List[Doc]]]: _description_
    """
    # Manually create copy since spacy spans cannot be deepcopied
    example_dicts = [d for d in examples]

    target_list: List[Doc] = []
    example_list: List[Doc] = []
    for _ in range(cv):
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
            criteria_keys,
            n_target,
            example_dicts,
        )
        example_list.append(
            [ex for prev_target in target_list for ex in prev_target]
            + extracted_examples,
        )
        target_list.append(extracted_targets)

    return target_list, example_list
