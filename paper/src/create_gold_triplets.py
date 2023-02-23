import json
from pathlib import Path
from typing import Any, Dict, List

import spacy
from spacy.tokens import Doc
from wasabi import msg

from conspiracies import PromptOutput, SpanTriplet


def read_prompts(path: Path) -> List[Dict[str, Any]]:
    """Reads prompts from a JSON file.

    Args:
        path (Path): Path to the JSON file.

    Returns:
        list: List of prompts.
    """
    with open(path, "r") as f:
        prompts = json.load(f)
    return prompts


def test_prompt(prompt: PromptOutput, nlp: spacy.Language, visualize: bool = False):
    doc = nlp(prompt.text)
    triplets = []
    for triplet in prompt.triplets:

        span_triplet = SpanTriplet.from_doc(doc=doc, triplet=triplet)

        if span_triplet is None:
            msg.warn(f"Could not find triplet {triplet} in {prompt.text}")
            continue
        # visualize the triplet
        if visualize:
            span_triplet.visualize()
        triplets.append(span_triplet)
    return doc, triplets


def doc_to_json(doc, triplets: List[SpanTriplet]):
    json = doc.to_json()
    json["semantic_triplets"] = [
        triplet.to_dict(include_doc=False) for triplet in triplets
    ]
    return json


def doc_from_json(json):
    doc = Doc.from_json(json)
    triplets = [
        SpanTriplet.from_dict(triplet_json)
        for triplet_json in json["semantic_triplets"]
    ]
    return doc, triplets


def __exact_span_match(t1, t2):
    if not (t1.subject.start, t1.subject.end) == (t2.subject.start, t2.subject.end):
        return False
    if not (t1.predicate.start, t1.predicate.end) == (
        t2.predicate.start,
        t2.predicate.end,
    ):
        return False
    if not (t1.object.start, t1.object.end) == (t2.object.start, t2.object.end):
        return False
    return True


def __exact_text_match(t1, t2):
    if not t1.subject.text == t2.subject.text:
        return False
    if not t1.predicate.text == t2.predicate.text:
        return False
    if not t1.object.text == t2.object.text:
        return False
    return True


def calc_metrics(
    gold_triplets: List[SpanTriplet], extracted_triplets: List[SpanTriplet]
):
    """ """
    metrics = {}

    gold_doc = gold_triplets[0].span.doc
    extracted_doc = extracted_triplets[0].span.doc
    assert gold_doc.text == extracted_doc.text, "The documents must be the same."

    metrics = {
        "n_extracted_triplets": len(extracted_triplets),
        "n_gold_triplets": len(gold_triplets),
        "n_exact_span_match": 0,
        "n_exact_text_match": 0,
    }

    # exact span match
    metrics["n_exact_span_match"] = 0
    for e_triplet in extracted_triplets:
        for i, g_triplet in enumerate(gold_triplets):
            if __exact_span_match(e_triplet, g_triplet):
                gold_triplets.pop(i)
                metrics["n_exact_span_match"] += 1
                break

    metrics["n_exact_text_match"] = 0
    for e_triplet in extracted_triplets:
        for i, g_triplet in enumerate(gold_triplets):
            if __exact_text_match(e_triplet, g_triplet):
                gold_triplets.pop(i)
                metrics["n_exact_text_match"] += 1
                break


if __name__ == "__main__":
    path = Path(__file__).parent.parent.parent / "data" / "gpt_predictions_compare.json"
    prompts = read_prompts(path)
    nlp = spacy.load("en_core_web_sm")

    visualize = False
    gold_extracted_triplets = []
    for i, prompt in enumerate(prompts):
        if visualize:
            msg.info(f"Processing prompt {i}")
        triplets = prompt["gold_tagging"]
        text = prompt["tweet"]
        prompt = PromptOutput(input_text=text, triplets=triplets)  # type: ignore
        output = test_prompt(prompt, nlp, visualize)  # type: ignore
        gold_extracted_triplets.append(output)

    template3_extracted_triplets = []
    for i, prompt in enumerate(prompts):
        if visualize:
            msg.info(f"Processing prompt {i}")
        triplets = prompt["template_3"]
        triplets = [t for t in triplets if len(t) == 3]
        text = prompt["tweet"]
        prompt = PromptOutput(input_text=text, triplets=triplets)  # type: ignore
        output = test_prompt(prompt, nlp, visualize)  # type: ignore
        template3_extracted_triplets.append(output)

    triplet = gold_extracted_triplets[0][1][0]
    exact_span_match(triplet, triplet)
    template3_extracted_triplets[0][1]

    # exact span match
    # precision
    # recall
    # f1
    # exact text match
    # precision
    # recall
    # f1
