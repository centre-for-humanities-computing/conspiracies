import pytest

from conspiracies.document import Document
from conspiracies.preprocessing.csv import CsvPreprocessor


@pytest.fixture
def csv_with_headers():
    lines = [
        "id,text,context,metadata1,metadata2",
        "1,some text,a bit of context,one,two",
    ]
    return lines


@pytest.fixture
def expected_docs():
    return [
        Document(
            id="1",
            text="some text",
            context="a bit of context",
            metadata={"metadata1": "one", "metadata2": "two"},
        ),
    ]


def test_read_lines(csv_with_headers, expected_docs):
    preprocessor = CsvPreprocessor(
        id_column="id",
        text_column="text",
        context_column="context",
    )
    # NOTE: metadata fields are not filtered in this method, so all other fields will be
    #   included as metadata
    assert list(preprocessor._read_lines(csv_with_headers)) == expected_docs
