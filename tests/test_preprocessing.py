from typing import Iterator

import pytest

from conspiracies.document import Document
from conspiracies.preprocessing.preprocessor import Preprocessor


@pytest.fixture
def docs() -> Iterator[Document]:
    # if using yield, the pytest fixture does not work quite as expected
    docs = []
    for i in range(2):
        docs.append(
            Document(
                id=str(i),
                text=f"text {i}",
                metadata={
                    "one": "something",
                    "two": "something else",
                },
                context=None,
            ),
        )
    return (d for d in docs)


def test_metadata_filtering_removes_field(docs):
    preprocessor = Preprocessor(metadata_fields={"one"})
    filtered = list(preprocessor._filter_metadata(docs))
    assert len(filtered) == 2
    for doc in filtered:
        assert "one" in doc["metadata"] and "two" not in doc["metadata"]


def test_metadata_filtering_retains_all(docs):
    preprocessor = Preprocessor(metadata_fields={"*"})
    filtered = list(preprocessor._filter_metadata(docs))
    assert len(filtered) == 2
    for doc in filtered:
        assert all(key in doc["metadata"] for key in ("one", "two"))
