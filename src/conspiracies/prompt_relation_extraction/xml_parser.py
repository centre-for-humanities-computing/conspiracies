"""
A script which parses semantic triplets froma a text which is annotated in an XLM.
The function parse() takes a string as input and returns a dict containing the keys,
"text" and "triplets". The value of "text" is the input string without the tags. The
value of "triplets" is a list of dicts, each containing the keys "subject", "predicate",
"object" and "n". 

Example:
    >>> text = "@Berry1952K: @BibsenSkyt @JakobEllemann Synes <subject-1>det</subject-1> <predicate-1>er</predicate-1> total <object-1>mangel på respekt</object-1> for alle andre partiledere."
    >>> parse(text)
    {
        "text": "@Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.",
        "triplets": [
            {
                    "subject": "det",
                    "predicate": "er",
                    "object": "total mangel på respekt for alle andre partiledere"
                    "n": 1
            }
        ]
    }
"""
import re
from collections import defaultdict
from typing import Tuple


def extract_tags(text, tags=["subject", "predicate", "object"]):
    """
    Extracts all tags on the form:
    <{tag}-{n}>{content}</{tag}-{n}>

    and returns a dict on the form:
    {tag: tag, span: (start, end), n: n, is_close: bool}
    """
    # create regex pattern to match both start and close tags
    pattern = r"<[/]?(" + "|".join(tags) + r")-\d+>"

    def extract_tag_info(match):
        tag = match.group()[1:-1]
        is_close = tag.startswith("/")
        if is_close:
            tag = tag[1:]
        tag, n = tag.split("-")
        return {"tag": tag, "span": match.span(), "n": n, "is_close": is_close}

    return [extract_tag_info(m) for m in re.finditer(pattern, text)]


def remove_tags(text):
    """remove all tags from a string"""
    return re.sub(r"<[/]?\w+-\d+>", "", text)


def update_span(span: Tuple[int, int], deleted_span: Tuple[int, int]):
    """updates a span by after a part of the text has been deleted"""

    diff = deleted_span[1] - deleted_span[0]

    # if deleted span is before span
    if span[0] >= deleted_span[1]:
        return -diff, -diff
    # if deleted span is after span
    if span[1] <= deleted_span[0]:
        return 0, 0
    # if deleted span is inside span
    if span[0] <= deleted_span[0] and span[1] >= deleted_span[1]:
        return 0, -diff
    # if deleted span is overlapping start of span
    if span[0] < deleted_span[0] and span[1] < deleted_span[1]:
        return 0, deleted_span[0] - span[1]
    # if deleted span is overlapping end of span
    if span[0] > deleted_span[0] and span[1] > deleted_span[1]:
        return deleted_span[1] - span[0], 0
    # if deleted span is equal to span
    if span[0] == deleted_span[0] and span[1] == deleted_span[1]:
        raise ValueError("Span to delete is equal to span to update")
    raise ValueError("Unknown error")


def parse(text: str, tags=["subject", "predicate", "object"]):
    tags_info = extract_tags(text, tags)

    open_tags = {}
    closed_tags = {}
    for tag_info in tags_info:
        n = tag_info["n"]
        tag = tag_info["tag"]
        if tag_info["is_close"]:
            closed_tags[f"{tag}-{n}"] = {"span": tag_info["span"]}
        else:
            open_tags[f"{tag}-{n}"] = {"span": tag_info["span"], "tag": tag, "n": n}

    # extract triplets
    triplets = defaultdict(lambda: {"subject": None, "predicate": None, "object": None})  # type: ignore
    spans_to_update = []
    for tag_n in open_tags:
        if tag_n in closed_tags:
            content_span = list(
                (open_tags[tag_n]["span"][1], closed_tags[tag_n]["span"][0])
            )
            content = text[content_span[0] : content_span[1]]
            tag = open_tags[tag_n]["tag"]
            n = open_tags[tag_n]["n"]
            triplets[n][tag] = {"text": remove_tags(content), "span": content_span}  # type: ignore
            spans_to_update.append(content_span)

    spans_to_remove = [tag_info["span"] for tag_info in tags_info]
    for span in spans_to_update:
        static_span = tuple(span)
        # print(span)
        content = text[span[0] : span[1]]
        # print(content)
        for span_to_remove in spans_to_remove:
            _span = update_span(static_span, span_to_remove)  # type: ignore
            span[0] += _span[0]
            span[1] += _span[1]
            # print("\t", span)

    return {"text": remove_tags(text), "triplets": triplets}


# text = "@Berry1952K: @BibsenSkyt @JakobEllemann Synes <subject-1>det</subject-1> <predicate-1>er</predicate-1> total <object-1>mangel på respekt</object-1> for alle andre partiledere."
# out = parse(text)
# text = out["text"]
# triplets = out["triplets"]
# print(triplets)

# test
# for n, triplet in triplets.items():
#     subject = triplet["subject"]["text"]
#     _subject = text[triplet["subject"]["span"][0] : triplet["subject"]["span"][1]]
#     assert subject == _subject

#     predicate = triplet["predicate"]["text"]
#     _predicate = text[triplet["predicate"]["span"][0] : triplet["predicate"]["span"][1]]
#     assert predicate == _predicate

#     obj = triplet["object"]["text"]
#     _obj = text[triplet["object"]["span"][0] : triplet["object"]["span"][1]]
#     assert obj == _obj
