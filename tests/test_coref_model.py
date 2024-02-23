from .utils import nlp_da, nlp_en  # noqa

from conspiracies.docprocessing.coref import CoreferenceModel


def test_da_coref_model(nlp_da):  # noqa
    model = CoreferenceModel.danish()  # check that the model loads as intended

    text = [
        "Hej Kenneth, har du en fed teksts vi kan skrive om dig?",
        "Ja, det kan du tro min fine ven.",
    ]
    docs = nlp_da.pipe(text)

    # test batches forward
    outputs = model.predict_batch_docs(docs)

    # test output format
    for output in outputs:
        assert isinstance(output, dict)


def test_en_coref_model(nlp_en):  # noqa
    model = CoreferenceModel.english()

    text = [
        "Luke Skywalker is from a moisture farm on Tatooine. "
        "He flees when the Empire comes to find C-3PO and R2-D2.",
    ]
    docs = nlp_en.pipe(text)

    # test batches forward
    outputs = model.predict_batch_docs(docs)

    # test output format
    for output in outputs:
        assert isinstance(output, dict)
