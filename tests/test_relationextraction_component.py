from conspiracies.relationextraction import SpacyRelationExtractor
import spacy

from .utils import nlp_da


def test_relationextraction_component(nlp_da):

    test_sents = [
        "Pernille Blume vinder delt EM-sølv i Ungarn.",
        "Pernille Blume blev nummer to ved EM på langbane i disciplinen 50 meter fri.",
        "Hurtigst var til gengæld hollænderen Ranomi Kromowidjojo, der sikrede sig guldet i tiden 23,97 sekunder.",
        "Og at formen er til en EM-sølvmedalje tegner godt, siger Pernille Blume med tanke på, at hun få uger siden var smittet med corona.",
        "Ved EM tirsdag blev det ikke til medalje for den danske medley for mixede hold i 4 x 200 meter fri.",
        "In a phone call on Monday, Mr. Biden warned Mr. Netanyahu that he could fend off criticism of the Gaza strikes for only so long, according to two people familiar with the call",
        "That phone call and others since the fighting started last week reflect Mr. Biden and Mr. Netanyahu’s complicated 40-year relationship.",
        "Politiet skal etterforske Siv Jensen etter mulig smittevernsbrudd.",
        "En av Belgiens mest framträdande virusexperter har flyttats med sin familj till skyddat boende efter hot från en beväpnad högerextremist.",
    ]

    # change these to your purposes. 2.7 is the default confidence threshold(the bulk of bad relations not kept and the majority of correct ones kept)
    # batch_size should be changed according to your device. Can most likely be bumped up a fair bit
    config = {"confidence_threshold": 2.7, "model_args": {"batch_size": 10}}
    nlp_da.add_pipe("relation_extractor", config=config)

    pipe = nlp_da.pipe(test_sents)

    for d in pipe:
        print(d.text, "\n", d._.relation_triplets)
