from pathlib import Path
from typing import List, Optional

import spacy
from conspiracies import docs_from_jsonl
from spacy.tokens import Doc


def load_gold_triplets(
    path: Optional[str] = None,
    nlp: Optional[spacy.Language] = None,
) -> List[Doc]:
    if nlp is None:
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


def load_api_key() -> str:
    path = Path("/data") / "conspiracies" / "api_key.txt"
    if not path.exists():
        raise FileNotFoundError(
            f"File {path} not found. You are probably not running this from Grundtvig"
            + ", in which case you will have to specify the path.",
        )
    with open(path, "r") as f:
        key = f.read()
    return key
