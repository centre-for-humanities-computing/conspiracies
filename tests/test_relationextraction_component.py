from conspiracies.relationextraction import SpacyRelationExtractor  # noqa F401

from .utils import nlp_da  # noqa F401


def test_relationextraction_component_pipe(nlp_da):  # noqa F811
    test_sents = [
        "Pernille Blume vinder delt EM-sølv i Ungarn.",
        "Pernille Blume blev nummer to ved EM på langbane i disciplinen 50 meter fri.",
    ]

    # change these to your purposes. 2.5 is the default confidence threshold(the bulk of
    # bad relations not kept and the majority of correct ones kept)
    # batch_size should be changed according to your device. Can most likely be bumped
    # up a fair bit
    config = {"confidence_threshold": 2.5, "model_args": {"batch_size": 10}}
    nlp_da.add_pipe("relation_extractor", config=config)

    pipe = nlp_da.pipe(test_sents)

    for d in pipe:
        print(d.text, "\n", d._.relation_triplets)


def test_relation_extraction_component_single(nlp_da):  # noqa F811
    nlp_da.add_pipe("relation_extractor")
    doc = nlp_da("Barack Obama is the former president of the United States")
    triplet_str = [
        tuple([str(t) for t in triplet]) for triplet in doc._.relation_triplets
    ]
    assert triplet_str == [
        ("Barack Obama", "is", "the former president of the United States"),
    ]


def test_relation_extraction_multi_sentence(nlp_da):  # noqa F811
    nlp_da.add_pipe("relation_extractor")
    doc = nlp_da(
        "Barack Obama is the former president of the United States. Du har to heste"
        + " der hedder Jens og Frode",
    )
    triplet_str = [
        tuple([str(t) for t in triplet]) for triplet in doc._.relation_triplets
    ]
    assert triplet_str == [
        ("Barack Obama", "is", "the former president of the United States"),
        ("Du", "har to heste", "der hedder Jens og Frode"),
    ]


def test_relation_extraction_empty_string(nlp_da):  # noqa F811
    nlp_da.add_pipe("relation_extractor")
    doc = nlp_da("")
    assert doc._.relation_triplets == []


def test_relation_extraction_no_extracted_relation(nlp_da):  # noqa F811
    nlp_da.add_pipe("relation_extractor")
    doc = nlp_da("Ingen relation")
    assert doc._.relation_triplets == []
