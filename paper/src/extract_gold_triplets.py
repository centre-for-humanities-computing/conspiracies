"""
extract gold triplets from annotation markdown
"""

from pathlib import Path
from typing import Any, Dict, List

import jsonlines
import spacy
from spacy.tokens import Doc
from wasabi import msg

from conspiracies import PromptOutput, SpanTriplet


def extract_from_annotations():
    path = (
        Path(__file__).parent.parent.parent
        / "data"
        / "prompt_outputs_compare_templates.md"
    )

    with open(path, "r") as f:
        text = f.read()

    tweets = text.split("#### Target tweet:")
    tweets = tweets[1:]

    tweet_triplets = []
    for tweet in tweets:
        text_table_comment = list(filter(lambda x: x, tweet.split("\n\n")))
        if len(text_table_comment) == 2:
            text, table = text_table_comment
            comment = ""
        elif len(text_table_comment) == 3:
            text, table, comment = text_table_comment
        else:
            raise ValueError("Invalid tweet format")

        # split table based on first column
        rows = [[r.strip() for r in row.split("|")[1:-1]] for row in table.split("\n")]
        rows = rows[2:]

        triplets: Dict[str, Any] = {}
        cat = ""
        for row in rows:
            if row:
                if row[0].startswith("**") and row[0].endswith("**"):
                    cat = row[0][2:-2].lower()
                    triplets[cat] = []

                assert len(row) == 4
                triplets[cat].append(row[1:])

        tweet_triplets.append((text, triplets, comment))

    return tweet_triplets


def test_prompt(prompt: PromptOutput, nlp: spacy.Language, visualize: bool = False):
    doc = nlp(prompt.text)
    triplets = []
    for triplet in prompt.triplets:

        span_triplet = SpanTriplet.from_doc(doc=doc, triplet=triplet)

        if span_triplet is None:
            msg.warn(f"Could not find triplet {triplet} in {prompt.text}")
            raise ValueError("Could not find triplet")
            # continue
        # visualize the triplet
        if visualize:
            span_triplet.visualize()
        triplets.append(span_triplet)
    return doc, triplets


nlp = spacy.load("en_core_web_lg")
triplets = extract_from_annotations()

# convert to PromptOutput
prompts = []
for text, triplets, comment in triplets:
    triplets_ = triplets["Gold updated (KCE)".lower()]
    triplets_ = [
        triplet for triplet in triplets_ if not any([t.strip() == "" for t in triplet])
    ]
    prompt = PromptOutput(input_text=text.strip(), triplets=triplets_)
    prompts.append(prompt)

# test
span_triplets = []
for i, prompt in enumerate(prompts):
    msg.info(f"Processing prompt {i}/{len(prompts)-1}")
    doc, triplets = test_prompt(prompt, nlp, visualize=True)
    span_triplets.append((doc, triplets))


# Correct triplets
doc, triplets = span_triplets[10]
triplet = triplets[-1]
triplet.subject = triplet.subject.doc[17:18]
triplet.subject.label_ = "SUBJECT"
triplets[-1] = triplet
span_triplets[10] = (doc, triplets)

doc, triplets = span_triplets[11]
triplet = triplets[2]
triplet.subject = triplet.subject.doc[15:16]
triplet.subject.label_ = "SUBJECT"
triplets[2] = triplet
triplet = triplets[3]
triplet.predicate = triplet.predicate.doc[21:22]
triplet.predicate.label_ = "PREDICATE"
triplets[3] = triplet
triplet = triplets[-1]
triplet.subject = triplet.subject.doc[34:35]
triplet.subject.label_ = "SUBJECT"
triplets[-1] = triplet

span_triplets[11] = (doc, triplets)

triplet.visualize()
# check triplet n
n = 29
doc, triplets = span_triplets[n]
t = test_prompt(prompts[n], nlp, visualize=True)


def doc_to_json(doc, triplets: List[SpanTriplet]):
    json = doc.to_json()
    json["semantic_triplets"] = [
        triplet.to_dict(include_doc=False) for triplet in triplets
    ]
    return json


def doc_from_json(json, nlp):
    doc = Doc(nlp.vocab).from_json(json)
    triplets = [
        SpanTriplet.from_dict(triplet_json, nlp=nlp, doc=doc)
        for triplet_json in json["semantic_triplets"]
    ]
    return doc, triplets


def docs_to_jsonl(docs, triplets, path):
    jsonl = [doc_to_json(doc, triplets_) for doc, triplets_ in zip(docs, triplets)]
    with jsonlines.open(path, "w") as writer:
        writer.write_all(jsonl)


def docs_from_jsonl(path, nlp):
    docs = []
    triplets = []
    with jsonlines.open(path, "r") as reader:
        for json in reader:
            doc, triplets = doc_from_json(json, nlp)
            docs.append(doc)
            triplets.append(triplets)
    return docs, triplets


data_path = Path(__file__).parent.parent.parent / "data"
docs, triplets = zip(*span_triplets)

from conspiracies import docs_to_jsonl

docs_to_jsonl(docs, triplets, data_path / "gold_triplets.jsonl")

from conspiracies import docs_from_jsonl

docs, triplets = docs_from_jsonl(data_path / "gold_triplets.jsonl", nlp=nlp)
