import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Iterator, Iterable, List, Union

from pydantic import BaseModel
from stop_words import get_stop_words

from conspiracies.common.fileutils import iter_lines_of_files


class TripletField(BaseModel):
    text: str
    start_char: Optional[int]
    end_char: Optional[int]
    head: Optional[str]

    def clear_head_if_blacklist_match(self, blacklist: Set[str]):
        if self.head and self.head in blacklist:
            self.head = None
        return self


class Triplet(BaseModel):
    subject: TripletField
    predicate: TripletField
    object: TripletField
    doc: Optional[str]
    timestamp: Optional[datetime]

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

    @staticmethod
    def filter_on_entity_label_frequency(
        triplets: Iterable["Triplet"],
        min_frequency: int,
        min_doc_frequency: int = 1,
    ):
        entity_label_counter = Counter(
            f.text for triplet in triplets for f in (triplet.subject, triplet.object)
        )
        docs = defaultdict(set)
        for triplet in triplets:
            for f in (triplet.subject, triplet.object):
                docs[f.text].add(triplet.doc)
        doc_frequency = {label: len(docs) for label, docs in docs.items()}

        filtered = [
            triplet
            for triplet in triplets
            if entity_label_counter[triplet.subject.text] >= min_frequency
            and entity_label_counter[triplet.object.text] >= min_frequency
            and doc_frequency[triplet.subject.text] >= min_doc_frequency
        ]
        return filtered

    @classmethod
    def from_annotated_docs(cls, path: Path) -> Iterator["Triplet"]:
        return (
            cls(
                **triplet_data,
                doc=json_data.get("id", None),
                timestamp=json_data.get("timestamp", None),
            )
            for json_data in (json.loads(line) for line in iter_lines_of_files(path))
            for triplet_data in json_data["semantic_triplets"]
        )

    @staticmethod
    def write_jsonl(path: Union[str, Path], triplets: Iterable["Triplet"]):
        with open(path, "w") as out:
            print(*(t.json() for t in triplets), file=out, sep="\n")
