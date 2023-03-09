from pathlib import Path
from typing import List, Tuple

import spacy
from spacy.tokens import Doc

from ..prompt_relation_extraction import SpanTriplet
from ..utils import docs_from_jsonl


def load_gold_triplets() -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    path = Path(__file__).parent / "gold_triplets.jsonl"
    docs, triplets = docs_from_jsonl(path, nlp)
    return docs, triplets
