from spacy.tokens import Doc
from spacy import Vocab

from conspiracies.docprocessing.relationextraction.multi2oie import multi2oie_utils


def test_relationextraction_doc_extension():
    """Verifies the behavior of the relation triplet extensions and the lambdas
    that back them."""
    multi2oie_utils.install_extensions()

    words = "this is a test".split()
    vocab = Vocab(strings=words)
    test_doc = Doc(vocab, words=words)

    head = test_doc[0:1]
    relation = test_doc[1:2]
    tail = test_doc[2:4]

    test_doc._.relation_head = [head]
    test_doc._.relation_relation = [relation]
    test_doc._.relation_tail = [tail]

    # verify the extension that contains the actual indices
    assert test_doc._.relation_head_idxs == [(0, 1)]
    assert test_doc._.relation_relation_idxs == [(1, 2)]
    assert test_doc._.relation_tail_idxs == [(2, 4)]

    # verify that relation_triplets are correctly built from the other extensions
    assert test_doc._.relation_triplets == [(head, relation, tail)]
