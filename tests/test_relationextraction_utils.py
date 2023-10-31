from spacy.tokens import Doc
from spacy import Vocab

from conspiracies.docprocessing.relationextraction.multi2oie import multi2oie_utils


def test_relationextraction_doc_extension():
    """Verifies the behavior of the relation triplet extension and the lambdas
    that back it."""
    multi2oie_utils.install_extensions()

    words = "this is a test . the test seems cool".split()
    vocab = Vocab(strings=words)
    test_doc = Doc(vocab, words=words)

    this = test_doc[0:1]
    is_ = test_doc[1:2]
    a_test = test_doc[2:4]
    the_test = test_doc[5:7]
    seems = test_doc[7:8]
    cool = test_doc[8:9]

    test_doc._.relation_triplets = [(this, is_, a_test), (the_test, seems, cool)]

    # check setter/getter mirroring
    assert test_doc._.relation_triplets == [
        (this, is_, a_test),
        (the_test, seems, cool),
    ]

    # check index extension
    assert test_doc._.relation_triplet_idxs == [
        ((0, 1), (1, 2), (2, 4)),
        ((5, 7), (7, 8), (8, 9)),
    ]

    # check heads, relations and tails
    assert test_doc._.relation_head == [this, the_test]
    assert test_doc._.relation_relation == [is_, seems]
    assert test_doc._.relation_tail == [a_test, cool]
