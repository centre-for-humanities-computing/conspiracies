from .utils import nlp_da  # noqa

from conspiracies.docprocessing.coref import CoreferenceModel


def test_CoreferenceModel(nlp_da):  # noqa
    model = CoreferenceModel()  # check that the model loads as intended

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
