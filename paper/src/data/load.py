from pathlib import Path
from typing import List, Optional, Tuple

import spacy
from spacy.tokens import Doc

from conspiracies import SpanTriplet, docs_from_jsonl


def load_gold_triplets(
    path: Optional[str] = None,
) -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")
    if path is None:
        path = "/data/conspiracies/gold_triplets/gold_triplets_tweet.jsonl"
    # check if it existing
    if not Path(path).exists():
        raise FileNotFoundError(
            f"File {path} not found. You are probably not running this from Grundtvig"
            + ", in which case you will have to specify the path.",
        )
    docs, triplets = docs_from_jsonl(path, nlp)
    return docs, triplets
