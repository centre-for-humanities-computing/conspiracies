"""extract examples of tweets and triplets examples are on ucloud in
data/triplet-extraction-gpt/tagged/"""

import random
import re
from typing import List
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
    # Manually create copy since spacy spans cannot be deepcopied
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
