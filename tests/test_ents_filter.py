import spacy
from spacy.tokens import Doc, Span

from conspiracies.docprocessing.headwordextraction.headwordextraction_component import (
    contains_ents,
)


def test_ents_filter():
    nlp = spacy.blank("en")
    nlp.add_pipe("heads_extraction")
    doc = Doc(nlp.vocab, words="Mette Frederiksen is the Danish Politician".split())
    doc.set_ents([Span(doc, 0, 2, "PERSON")])

    assert contains_ents(doc[:]) is True
    assert contains_ents(doc[1:2]) is True
    assert contains_ents(doc[2:4]) is False
