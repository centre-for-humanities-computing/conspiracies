import conspiracies  # noqa F401

from .utils import nlp_en  # noqa F401


def test_most_common_ancestor(nlp_en):  # noqa F811
    nlp_en.add_pipe(
        "heads_extraction",
        config={"normalize_to_entity": False, "normalize_to_noun_chunk": False},
    )
    doc = nlp_en("Mette Frederiksen is the Danish politician.")

    assert doc[0:1]._.most_common_ancestor.text == "Mette"  # Single token Span
    assert doc[0:2]._.most_common_ancestor.text == "Frederiksen"  # Span
    assert doc._.most_common_ancestor.text == "is"  # Doc

    # remove the pipe
    nlp_en.remove_pipe("heads_extraction")
    nlp_en.add_pipe(
        "heads_extraction",
        config={
            "force": True,
            "normalize_to_entity": True,
            "normalize_to_noun_chunk": True,
        },
    )

    assert (
        doc[0:1]._.most_common_ancestor.text == "Mette Frederiksen"
    )  # Single token Span
    assert doc[0:2]._.most_common_ancestor.text == "Mette Frederiksen"  # Span
    assert doc._.most_common_ancestor.text == "is"  # Doc
