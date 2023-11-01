import numpy as np
from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    score_open_relations,
)
from spacy.training import Example

from .utils import docs_with_triplets  # noqa F401


def test_prompt_relation_evaluate(docs_with_triplets):  # noqa: F811
    # TODO: the document references in Span and Triple objects go all over the place
    #  through this test

    docs = docs_with_triplets

    keys = [
        "exact_span_match",
        "exact_string_match",
        "normalized_span_overlap",
        "normalized_string_overlap",
    ]

    # # perfect match
    doc = docs[0]
    example = Example(doc, doc)
    score = score_open_relations([example])

    for key in keys:
        assert score[f"{key}_f1"] == 1.0
        assert score[f"{key}_precision"] == 1.0
        assert score[f"{key}_recall"] == 1.0

    # no match
    doc_no_triplets = doc[:].as_doc()
    doc_no_triplets._.relation_triplets = DocTriplets(
        span_triplets=[],
        doc=doc_no_triplets,
    )
    example = Example(reference=doc, predicted=doc_no_triplets)
    score = score_open_relations([example])

    assert score["n_predictions"] == 0
    assert score["n_references"] == 3
    for key in keys:
        assert np.isnan(score[f"{key}_f1"])
        assert np.isnan(score[f"{key}_precision"])
        assert score[f"{key}_recall"] == 0.0

    # partial match
    doc_partial_match = doc[:].as_doc()
    triplet = doc._.relation_triplets[0]
    doc_partial_match._.relation_triplets = DocTriplets(
        span_triplets=[triplet],
        doc=doc_partial_match,
    )

    example = Example(reference=doc, predicted=doc_partial_match)
    score = score_open_relations([example])

    for key in keys:
        assert 1 > score[f"{key}_f1"] > 0
        assert score[f"{key}_recall"] - 0.333 < 0.01
        assert score[f"{key}_precision"] == 1

    # partial match (overmatched)
    example = Example(predicted=doc, reference=doc_partial_match)
    score = score_open_relations([example])

    for key in keys:
        assert 1 > score[f"{key}_f1"] > 0
        assert score[f"{key}_recall"] == 1
        assert score[f"{key}_precision"] - 0.333 < 0.01
