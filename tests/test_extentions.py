from .utils import nlp_en  # noqa

from spacy.tokens import Span

import conspiracies  # noqa


def test_extentions(nlp_en):  # noqa
    nlp_en.add_pipe("heads_extraction")

    doc = nlp_en("Mette Frederiksen is the Danish Politician")
    doc.set_ents([Span(doc, 0, 2, "PERSON")])

    assert isinstance(doc._.most_common_ancestor, Span)  # Doc
    assert isinstance(doc[0:2]._.most_common_ancestor, Span)  # Span
