import json

import bs4

from conspiracies.common.fileutils import iter_lines_of_files
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

    def _do_preprocess_docs(self, glob_pattern: str):
        lines = iter_lines_of_files(glob_pattern)
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
