from pathlib import Path
from typing import List, Optional

import spacy
from conspiracies import docs_from_jsonl
from spacy.tokens import Doc


def load_gold_triplets(
    path: Optional[str] = None,
) -> List[Doc]:
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
    return docs_from_jsonl(path, nlp)
