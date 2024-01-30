from typing import Iterator

import ndjson

from conspiracies.document import Document


class Preprocessor:
    def __init__(self, n_cores: int = 1):
        self.n_cores = n_cores

    def preprocess_docs(self, input_path: str, output_path: str, *args):
        preprocessed_docs = self.do_preprocess_docs(input_path)
        with open(output_path, "w+") as out_file:
            ndjson.dump(preprocessed_docs, out_file)

    def do_preprocess_docs(self, *args) -> Iterator[Document]:
        pass
