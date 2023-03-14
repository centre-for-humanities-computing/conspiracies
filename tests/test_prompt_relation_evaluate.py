""""""

from copy import copy

from conspiracies.prompt_relation_extraction import score_open_relations
from spacy.training import Example

from .utils import docs_with_triplets  # noqa F401


def test_prompt_relation_evaluate(docs_with_triplets):  # noqa: F811
    docs = docs_with_triplets

    keys = [
        "exact_span_match",
        "exact_text_match",
        "normalized_span_overlap",
        "normalized_char_overlap",
    ]

    # perfect match
    doc = docs[0]
    example = Example(doc, doc)
    score = score_open_relations([example])

    for key in keys:
        assert score[f"{key}_f1_macro"] == 1.0
        assert score[f"{key}_f1_micro"] == 1.0
        assert score[f"{key}_precision"] == 1.0
        assert score[f"{key}_recall"] == 1.0

    # no match
    doc_no_triplets = copy(doc)
    doc_no_triplets._.relation_triplets = []
    example = Example(doc, doc_no_triplets)
    score = score_open_relations([example])

    assert score["n_predictions"] == 0
    assert score["n_references"] == 2  # TODO: assumed, fix with actual
    assert score["f1_macro"] == 0.0
    assert score["f1_micro"] == 0.0
    assert score["recall"] == 0.0

    # partial match
    doc_partial_match = copy(doc)
    doc_partial_match._.relation_triplets = doc._.relation_triplets[:1]

    example = Example(doc, doc_partial_match)
    score = score_open_relations([example])

    assert 1 > score["f1_macro"] > 0
    assert 1 > score["f1_macro"] > 0
    assert score["precision"] == 1.0
    assert score["recall"] == 0.5
