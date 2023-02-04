from spacy.tokens import Span

import conspiracies  # noqa F401

from .utils import nlp_en  # noqa F401


def test_normalize_to_span(nlp_en):  # noqa F811
    nlp_en.add_pipe(
        "heads_extraction",
        config={
            "force": True,
            "normalize_to_entity": False,
            "normalize_to_noun_chunk": False,
        },
    )

    doc = nlp_en("Mette Frederiksen is the Danish politician.")

    normalized_token = doc[0]._.to_span  # Token

    assert isinstance(normalized_token, Span)
    assert normalized_token.text == "Mette"

    normalized_token = doc[0:2]._.to_span  # Span

    assert isinstance(normalized_token, Span)
    assert normalized_token.text == "Mette Frederiksen"

    normalized_token = doc._.to_span  # Doc

    assert isinstance(normalized_token, Span)
    assert normalized_token.text == "Mette Frederiksen is the Danish politician."


def test_normalize_to_entity(nlp_en):  # noqa F811
    nlp_en.add_pipe(
        "heads_extraction",
        config={
            "normalize_to_entity": True,
            "normalize_to_noun_chunk": False,
            "force": True,
        },
    )

    doc = nlp_en("Mette Frederiksen is the Danish politician.")

    normalized_token = doc[0]._.to_span

    assert isinstance(normalized_token, Span)
    assert normalized_token.text == "Mette Frederiksen"


def test_normalize_to_noun_chunk(nlp_en):  # noqa F811
    nlp_en.add_pipe(
        "heads_extraction",
        config={
            "normalize_to_noun_chunk": True,
            "normalize_to_entity": False,
            "force": True,
        },
    )

    doc = nlp_en("Mette Frederiksen is the Danish politician.")

    noun_chunk = doc[1]._.to_span

    assert isinstance(noun_chunk, Span)
    assert noun_chunk.text == "Mette Frederiksen"
    assert noun_chunk.text == "Mette Frederiksen"
