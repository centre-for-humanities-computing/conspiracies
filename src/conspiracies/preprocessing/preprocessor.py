import os.path
from os import path
import glob
from typing import List, Iterator

import ndjson

from conspiracies.document import Document


class Preprocessor:
    def __init__(
        self,
        project_name: str,
        output_folder: str = "output",
        n_cores: int = 1,
        batch_size=10000,
    ):
        self.project_name = project_name
        self.output_folder = output_folder
        self.n_cores = n_cores
        self.batch_size = batch_size
        self.at_batch = 0

    def preprocess_docs(self, *args):
        preprocessed_docs = self.do_preprocess_docs(*args)
        self.output_preprocessed_docs(preprocessed_docs)

    def do_preprocess_docs(self, *args) -> Iterator[Document]:
        pass

    def output_preprocessed_docs(self, preprocessed_docs: Iterator[Document]) -> None:
        p = path.join(self.output_folder, self.project_name)
        os.makedirs(p, exist_ok=True)
        batch = []
        for d in preprocessed_docs:
            batch.append(d)
            if len(batch) == self.batch_size:
                self.output_batch(batch)
                batch.clear()

    def output_batch(self, batch: List[Document]):
        filepath = path.join(
            self.output_folder,
            self.project_name,
            f"part{self.at_batch}.ndjson",
        )
        with open(filepath, "w+") as out_file:
            ndjson.dump(batch, out_file)
        self.at_batch += 1

    @staticmethod
    def iter_lines_of_files(glob_pattern: str):
        files = glob.glob(glob_pattern, recursive=True)
        for file in files:
            with open(file) as f:
                for line in f:
                    yield line
