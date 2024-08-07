import logging
from pathlib import Path
from typing import Iterator, Iterable

from conspiracies.document import Document


class Preprocessor:
    def __init__(self, metadata_fields: Iterable[str] = ("*",)):
        """
        Args:
            metadata_fields: fields in metadata dict to retain. If '*' is given,
                all fields will be retained.
        """
        self.metadata_fields = set(metadata_fields)

    def _do_preprocess_docs(self, input_path: Path) -> Iterator[Document]:
        pass

    def _filter_metadata(
        self,
        preprocessed_docs: Iterator[Document],
    ) -> Iterator[Document]:
        if "*" in self.metadata_fields:
            for doc in preprocessed_docs:
                yield doc

        for doc in preprocessed_docs:
            metadata = doc.metadata
            for key in list(metadata.keys()):
                if key not in self.metadata_fields:
                    del metadata[key]
            yield doc

    @staticmethod
    def _validate_content(
        preprocessed_docs: Iterator[Document],
    ) -> Iterator[Document]:
        for doc in preprocessed_docs:
            if not doc.text:
                logging.warning(
                    "Skipping doc with id '%s' because of empty text field",
                    doc.id,
                )
                continue
            else:
                yield doc

    def preprocess_docs(self, input_path: Path, output_path: Path, n_docs: int = None):
        preprocessed_docs = self._do_preprocess_docs(input_path)
        validated = self._validate_content(preprocessed_docs)
        if n_docs and n_docs > 0:
            validated = (d for i, d in enumerate(validated) if i < n_docs)
        metadata_filtered = self._filter_metadata(validated)

        with output_path.open("w+") as out_file:
            print(*(d.json() for d in metadata_filtered), file=out_file, sep="\n")
