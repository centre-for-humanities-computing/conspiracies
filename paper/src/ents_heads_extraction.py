"""Pipeline for headwords/entities extractions and frequency count."""

import multiprocessing
import os

import spacy
import torch
from tqdm import tqdm

from conspiracies.docprocessing.headwordextraction import contains_ents


def main():
    nlp = spacy.load("en_core_web_lg")

    test_sents = ["Mette Frederiksen is the Danish politician."] * 1000

    config = {"confidence_threshold": 2.7, "model_args": {"batch_size": 10}}
    nlp.add_pipe("relation_extractor", config=config)
    nlp.add_pipe("heads_extraction")

    # multiprocessing and torch with multiple threads result in a deadlock
    torch.set_num_threads(1)

    pipe = nlp.pipe(test_sents, n_process=os.cpu_count(), batch_size=25)

    heads_spans = []
    ents_spans = []

    for d in tqdm(pipe):
        for span in d._.relation_head:
            heads_spans.append(span._.most_common_ancestor)
            if span.ents:
                ents_spans.append(list(span.ents))
        for span in d._.relation_tail:
            heads_spans.append(span._.most_common_ancestor)
            if span.ents:
                ents_spans.append(list(span.ents))

    # Filter out headwords without an entity type
    filtered_heads = list(filter(contains_ents, heads_spans))

    # Flatten the list with ents
    flat_ents_list = [ent for sublist in ents_spans for ent in sublist]


if __name__ == "__main__":
    main()
