from typing import TypedDict


class Document(TypedDict):
    id: str
    metadata: dict
    text: str
    context: str


CONTEXT_END_MARKER = "[CONTEXT_END]"


def text_with_context(doc: Document) -> str:
    return "\n".join([doc["context"], CONTEXT_END_MARKER, doc["text"]])


def remove_context(text: str) -> str:
    return text.split(CONTEXT_END_MARKER)[-1]
