import json
import multiprocessing.pool

import bs4

from conspiracies.document import Document
from conspiracies.preprocessing.preprocessor import Preprocessor


class InfoMediaPreprocessor(Preprocessor):
    METADATA_KEYS = {
        "ArticleUrl",
        "Authors",
        "Heading",
        "Lead",
        "PageIds",
        "PublishDate",
        "Section",
        "Source",
        "WordCount",
    }

    def do_preprocess_docs(self, glob_pattern: str):
        lines = Preprocessor.iter_lines_of_files(glob_pattern)
        if self.n_cores > 1:
            with multiprocessing.pool.Pool(processes=self.n_cores) as p:
                for result in p.imap_unordered(self.process_line, lines, chunksize=100):
                    yield result
        else:
            for line in lines:
                yield self.process_line(line)

    def process_line(self, line: str):
        obj = json.loads(line)

        doc_id = obj["ArticleId"]
        metadata = {k: obj[k] for k in InfoMediaPreprocessor.METADATA_KEYS}
        text = self.create_text(obj)

        return Document(id=doc_id, metadata=metadata, text=text, context=None)

    @staticmethod
    def create_text(doc_obj: dict):
        text_pieces = [doc_obj["Heading"] + "\n"]

        subheading = doc_obj["SubHeading"]
        if subheading:
            text_pieces.append(subheading + "\n")

        body = bs4.BeautifulSoup(doc_obj["BodyText"], features="html.parser")
        paragraphs = body.find_all("p")
        for paragraph in paragraphs:
            paragraph_pieces = []
            for child in paragraph:
                if child.name == "br":
                    paragraph_pieces.append("\n")
                else:
                    paragraph_pieces.append(child.get_text())
            text_pieces.append("".join(paragraph_pieces))
        return "\n".join(text_pieces).strip()
