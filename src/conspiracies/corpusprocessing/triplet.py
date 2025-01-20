import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Set, Iterator, Iterable, Union, Literal

from pydantic import BaseModel
from stop_words import get_stop_words
from tqdm import tqdm

from conspiracies.common.fileutils import iter_lines_of_files


class TokenInfo(BaseModel):
    text: str
    lemma: str
    pos: str


class TripletField(BaseModel):
    text: str
    start_char: int
    end_char: int
    lemma: str
    tokens: list[TokenInfo]
    max_entity: str

    # TODO: this trimming function is, for now, created to work with English and should be tested with Danish.
    #  also, all language-specific stuff liket this should be done during docprocessing.

    def trimmed_and_normalized(
        self,
        field_type: Union[Literal["entity"], Literal["relation"]],
    ):
        """Trims triplet fields from regular function words and normalizes to lowercase lemma, e.g.:
        a cat -> cat
        the cats -> cat
        from the cats -> cat
        will take -> take
        has taken -> take
        """
        if field_type == "entity":
            main_words = {"NOUN", "PROPN"}
            function_words = {"DET", "ADP", "ADV", "PRON", "SCONJ", "CCONJ"}
        elif field_type == "relation":
            main_words = {"VERB"}
            function_words = {"AUX", "PART"}
        else:
            raise TypeError("Type must be 'entity' or 'relation'!")

        trimmed_tokens = list(self.tokens)
        # do not trim if everything is tagged as function words
        if not all(t.pos in function_words for t in self.tokens) or not any(
            t.pos in main_words for t in self.tokens
        ):
            while len(trimmed_tokens) > 1 and trimmed_tokens[0].pos in function_words:
                trimmed_tokens.pop(0)
            while len(trimmed_tokens) > 1 and trimmed_tokens[-1].pos in function_words:
                trimmed_tokens.pop()

        filtered_tokens = [
            t for t in trimmed_tokens if t.pos not in {"PUNCT", "X", "SPACE"}
        ]
        if not filtered_tokens:  # safeguard in case of weird extractions
            filtered_tokens = trimmed_tokens

        return " ".join(t.lemma.lower() for t in filtered_tokens)


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

    def has_blacklist_match(self, blacklist: Set[str]):
        return any(
            all(word in blacklist for word in text_field.lower().split())
            for text_field in self.text_fields()
        )

    @staticmethod
    def filter_on_label_length(
        triplets: Iterable["Triplet"],
        max_length: int,
    ) -> Iterator["Triplet"]:
        return (
            triplet
            for triplet in triplets
            if not any(
                len(text_field) > max_length for text_field in triplet.text_fields()
            )
        )

    @staticmethod
    def filter_on_stopwords(
        triplets: Iterable["Triplet"],
        language: str,
    ) -> Iterator["Triplet"]:
        stopwords = set(get_stop_words(language))
        return (
            triplet
            for triplet in triplets
            if not triplet.has_blacklist_match(stopwords)
        )

    @staticmethod
    def filter_on_entity_label_frequency(
        triplets: Iterable["Triplet"],
        min_frequency: int,
        min_doc_frequency: int = 1,
    ):
        # FIXME: This method cuts away the long tail of infrequent entities and their
        #  triplets. That is all nice and good, but as those are cut away, some entities
        #  will fall below those thresholds
        triplets = list(triplets)
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
            and doc_frequency[triplet.object.text] >= min_doc_frequency
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
            for json_data in tqdm(
                (json.loads(line) for line in iter_lines_of_files(path)),
                desc="Loading triplets",
            )
            for triplet_data in json_data["semantic_triplets"]
        )

    @staticmethod
    def write_jsonl(path: Union[str, Path], triplets: Iterable["Triplet"]):
        with open(path, "w") as out:
            print(*(t.json() for t in triplets), file=out, sep="\n")
