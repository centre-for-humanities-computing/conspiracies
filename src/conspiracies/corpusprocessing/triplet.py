import json
from typing import Optional, Set, Iterator, Iterable, List

from jsonlines import jsonlines
from pydantic import BaseModel
from stop_words import get_stop_words

from conspiracies.common.fileutils import iter_lines_of_files


class TripletField(BaseModel):
    text: str
    head: Optional[str]

    def clear_head_if_blacklist_match(self, blacklist: Set[str]):
        if self.head and self.head in blacklist:
            self.head = None
        return self


class Triplet(BaseModel):
    subject: TripletField
    predicate: TripletField
    object: TripletField

    def fields(self):
        return self.subject, self.predicate, self.object

    def text_fields(self):
        return (f.text for f in self.fields())

    def clear_field_heads_if_blacklist_match(self, blacklist: Set[str]):
        for field in self.fields():
            field.clear_head_if_blacklist_match(blacklist)
        return self

    def has_blacklist_match(self, blacklist: Set[str]):
        return any(text_field.lower() in blacklist for text_field in self.text_fields())

    @staticmethod
    def filter_on_stopwords(
        triplets: Iterable["Triplet"],
        language: str,
    ) -> List["Triplet"]:
        stopwords = set(get_stop_words(language))
        return [
            triplet.clear_field_heads_if_blacklist_match(stopwords)
            for triplet in triplets
            if not triplet.has_blacklist_match(stopwords)
        ]

    @classmethod
    def from_annotated_docs(cls, path: str) -> Iterator["Triplet"]:
        return (
            cls(**triplet_data)
            for line in iter_lines_of_files(path)
            for triplet_data in json.loads(line)["semantic_triplets"]
        )

    @staticmethod
    def write_jsonl(path: str, triplets: Iterable["Triplet"]):
        with jsonlines.open(path, "w") as out:
            out.write_all(map(Triplet.dict, triplets))
