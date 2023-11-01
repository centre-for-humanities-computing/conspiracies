from typing import Dict, List, Tuple, Union

from spacy.tokens import Doc
from thinc.types import Ragged
from transformers import BertTokenizer
from functools import cache

from conspiracies.docprocessing.relationextraction.data_classes import SpanTriplet


#### Wordpiece <-> spacy alignment functions
def wp2tokid(align: Ragged) -> Dict[int, int]:
    """Gets the wordpiece to token id mapping."""
    wp2tokid = []
    for i, length in enumerate(align.lengths):
        wp2tokid += length * [i]

    return {int(wp_id): t_id for wp_id, t_id in zip(align.data, wp2tokid)}


def get_wp_span_tuple(span: List[int]) -> Union[Tuple[int, int], str]:
    """Converts the relation span to a tuple, assumes that extractions are
    contiguous."""
    if not span:
        return ""
    if len(span) == 1:
        return (span[0], span[0])
    else:
        return (span[0], span[-1])


def wp_to_token_id_mapping(
    span: Tuple[int, int],
    wp_tokenid_mapping: Dict[int, int],
) -> Tuple[int, int]:
    """Converts wordpiece spans to token ids."""
    if span:
        return (wp_tokenid_mapping[span[0]], wp_tokenid_mapping[span[1]])
    else:
        return ""


def token_span_to_spacy_span(span: Tuple[int, int], doc: Doc):
    """Converts token id span to span."""
    if not span:
        return ""
    else:
        return doc[span[0] : span[1] + 1]


def wp_span_to_token(
    relation_span: List[List[int]],
    wp_tokenid_mapping: Dict,
    doc: Doc,
) -> List[SpanTriplet]:
    """Converts the wp span for each relation to spans.

    Assumes that relations are contiguous
    """
    relations = []  # type: ignore
    for triplet in relation_span:
        # convert list of wordpieces in the extraction to a tuple of the span (start,
        # end)
        head = get_wp_span_tuple(triplet[0])  # type: ignore
        relation = get_wp_span_tuple(triplet[1])  # type: ignore
        tail = get_wp_span_tuple(triplet[2])  # type: ignore

        # convert the wp span to token span
        head = wp_to_token_id_mapping(head, wp_tokenid_mapping)  # type: ignore
        relation = wp_to_token_id_mapping(relation, wp_tokenid_mapping)  # type: ignore
        tail = wp_to_token_id_mapping(tail, wp_tokenid_mapping)  # type: ignore

        # convert token span to spacy span
        head = token_span_to_spacy_span(head, doc)
        relation = token_span_to_spacy_span(relation, doc)
        tail = token_span_to_spacy_span(tail, doc)

        relations.append(SpanTriplet(subject=head, predicate=relation, object=tail))
    return relations


def match_extraction_spans_to_wp(
    extraction_spans: List[List[List[List[str]]]],
    wordpieces: List[str],
):
    """Correct the extracted spans from the model to match wordpieces in
    sentences that are not the first.

    Args:
        extraction_spans (List[List[List[List[str]]]]): The extracted spans
        wordpieces (List[str]): Wordpieces
    """
    max_wp_idx = 0
    matched_extractions = []
    for i, sent_span in enumerate(extraction_spans):
        new_spans = []
        if i > 0:
            max_wp_idx += len(wordpieces[i - 1])
        for triplet in sent_span:
            trip = []
            for relation_type in triplet:
                rel = []
                for val in relation_type:
                    rel.append(val + max_wp_idx)  # type: ignore
                trip.append(rel)
            new_spans.append(trip)

        matched_extractions += new_spans
    return matched_extractions


@cache
def get_cached_tokenizer(model_name):
    return BertTokenizer.from_pretrained(model_name)
