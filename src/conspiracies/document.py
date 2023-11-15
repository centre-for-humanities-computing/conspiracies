from typing import TypedDict


class Document(TypedDict):
    id: str
    metadata: dict
    text: str
    context: str
