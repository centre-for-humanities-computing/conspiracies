import glob
import os.path

from conspiracies.document import Document
from conspiracies.preprocessing.preprocessor import Preprocessor


class TextFilePreprocessor(Preprocessor):

    def __init__(self, basename_as_id=True):
        super().__init__()
        self.basename_as_id = basename_as_id

    def _do_preprocess_docs(self, glob_pattern: str):
        files = glob.glob(glob_pattern, recursive=True)
        for file in files:
            id_ = os.path.basename(file) if self.basename_as_id else file
            with open(file) as in_file:
                text = in_file.read()
            yield Document(
                id=id_,
                text=text,
                metadata={},
                context=None,
            )
