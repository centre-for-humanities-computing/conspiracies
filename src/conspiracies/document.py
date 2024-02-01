from typing import TypedDict, Optional


class Document(TypedDict):
    id: str
    metadata: dict
    text: str
    context: Optional[str]


CONTEXT_END_MARKER = "[CONTEXT_END]"


def text_with_context(doc: Document) -> str:
    if doc["context"] is None:
        return doc["text"]
    return "\n".join([doc["context"], CONTEXT_END_MARKER, doc["text"]])


def remove_context(text: str) -> str:
    return text.split(CONTEXT_END_MARKER)[-1].strip()
