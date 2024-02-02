import csv
from typing import Iterable, Iterator

from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.document import Document
from conspiracies.preprocessing.preprocessor import Preprocessor


class CsvPreprocessor(Preprocessor):

    def __init__(
        self,
        id_column: str = None,
        text_column: str = None,
        context_column: str = None,
        delimiter=",",
        metadata_fields: Iterable[str] = ("*",),
    ):
        self.id_column = id_column
        self.text_column = text_column
        self.context_column = context_column
        self.non_metadata_columns = {
            self.id_column,
            self.text_column,
            self.context_column,
        }
        self.delimiter = delimiter
        super().__init__(metadata_fields=metadata_fields)

    def _read_lines(self, lines: Iterable[str]) -> Iterator[str]:
        reader = csv.DictReader(lines, delimiter=self.delimiter)
        for row in reader:  # type: dict
            id_ = row[self.id_column]
            text = row[self.text_column]
            context = row[self.context_column] if self.context_column else None
            metadata = {
                k: v for k, v in row.items() if k not in self.non_metadata_columns
            }
            yield Document(
                id=id_,
                text=text,
                context=context,
                metadata=metadata,
            )

    def _do_preprocess_docs(self, input_path: str) -> Iterator[str]:
        lines = iter_lines_of_files(input_path)
        return self._read_lines(lines)
