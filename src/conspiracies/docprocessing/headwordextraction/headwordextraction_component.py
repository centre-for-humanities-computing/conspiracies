"""Headwords extraction as a spaCy component."""

from collections import Counter
from typing import Union
from warnings import warn

from spacy.language import Language
from spacy.tokens import Doc, Span, Token


class HeadwordsExtractionComponent:
    """A class for extracting headwords from a given text document.

    Args:
        nlp (Language): Language processing pipelines.
        name (str): The instance name of the component in the pipeline.

    Attributes:
        raise_error (bool): If True, raises warning message in case no ancestor is found
            within a span.
        normalize_to_entity (bool): If True, normalizes a token to an entity.
        normalize_to_noun_chunk (bool): If True, normalizes a token to a noun chunk.
    """

    def __init__(
        self,
        nlp: Language,
        name: str,
        raise_error: bool,
        normalize_to_entity: bool,
        normalize_to_noun_chunk: bool,
        force: bool,
    ):
        """Initialise components."""

        self.raise_error = raise_error
        self.normalize_to_entity = normalize_to_entity
        self.normalize_to_noun_chunk = normalize_to_noun_chunk
        self.name = name

        if not Token.has_extension("to_span") or force:
            Token.set_extension("to_span", getter=self.to_span, force=force)
        if not Span.has_extension("to_span") or force:
            Span.set_extension("to_span", getter=lambda span: span, force=force)
        if not Doc.has_extension("to_span") or force:
            Doc.set_extension("to_span", getter=lambda doc: doc[:], force=force)

        if (not Doc.has_extension("most_common_ancestor")) or force:
            Doc.set_extension(
                "most_common_ancestor",
                getter=lambda doc: self.most_common_ancestor(doc[:]),
                force=force,
            )
        if (not Span.has_extension("most_common_ancestor")) or force:
            Span.set_extension(
                "most_common_ancestor",
                getter=self.most_common_ancestor,
                force=force,
            )

    def to_entity(self, token: Token) -> Span:  # type: ignore
        """Normalize token to an entity.

        Args:
            token(Token): The token to normalize.

        Returns:
            Span: The entity.
        """
        for ent in token.doc.ents:
            if token in ent:
                return ent

    def to_noun_chunk(self, token: Token) -> Span:  # type: ignore
        """Normalize token to a noun chunk.

        Args:
            token(Token): The token to normalize.

        Returns:
            Span: The noun chunk.
        """
        doc = token.doc
        for noun_chunk in doc.noun_chunks:
            if token in noun_chunk:
                return noun_chunk

    def to_span(self, token: Union[Token, Span, Doc]) -> Span:
        """Normalize token to a span.

        Args:
            token(Token): The token to normalize.

        Returns:
            Span: The normalized token.
        """
        if self.normalize_to_entity:
            ent = self.to_entity(token)  # type: ignore
            if ent:
                return ent

        if self.normalize_to_noun_chunk:
            noun_chunk = self.to_noun_chunk(token)  # type: ignore
            if noun_chunk:
                return noun_chunk

        doc = token.doc
        return doc[token.i : token.i + 1]  # type: ignore

    def most_common_ancestor(
        self,
        span: Union[Doc, Span],
        raise_error: bool = False,
    ) -> Span:
        """Find the most common ancestor in a span.

        Args:
           span(Span): The span to find the most common ancestor of.
           raise_error(bool): Raises warning message if no ancestor is found within a
            span.

        Returns:
            Span: The most common ancestor of the span.
        """
        ancestors_in_span = Counter(
            [
                ancestor
                for token in span
                for ancestor in token.ancestors
                if ancestor in span
            ],
        )
        most_common_ancestors = ancestors_in_span.most_common()
        if most_common_ancestors:
            most_common_ancestor = most_common_ancestors[0][0]
        else:  # fall back is to simply take the first token
            most_common_ancestor = span[0]

        normalized_token = self.to_span(most_common_ancestor)

        if len(normalized_token) != 1:
            error_message = (
                f"None of the tokens in the span ({span}) contains an"
                + " ancestor within this span."
            )

            if raise_error:
                warn(error_message)

        return normalized_token

    def __call__(self, doc: Doc):
        """Run the pipeline component."""
        return doc


def contains_ents(span: Union[Doc, Span]) -> bool:
    """Check if a Doc or span contains entities.

    Args:
        span (Union[Doc, Span]): The span to find entites in.

    Returns:
        bool: Returns True if a token has an entity label.
    """
    for token in span:
        if token.ent_type:
            return True
    return False


@Language.factory(
    "heads_extraction",
    default_config={
        "raise_error": False,
        "normalize_to_entity": True,
        "normalize_to_noun_chunk": True,
        "force": True,
    },
)
def create_headwords_component(
    nlp: Language,
    name: str,
    raise_error: bool,
    normalize_to_entity: bool,
    normalize_to_noun_chunk: bool,
    force: bool,
) -> HeadwordsExtractionComponent:
    """Allows HeadwordsExtraction to be added to a spaCy pipe using
    nlp.add_pipe("heads_extraction").

    Args:
        nlp (Language): Language processing pipelines.

        name (str): The instance name of the component in the pipeline.
        raise_error (bool): If True, raises warning message in case no ancestor is found
            within a span.
        normalize_to_entity (bool): If True, normalizes a token to an entity.
        normalize_to_noun_chunk (bool): If True, normalizes a token to a noun chunk.

    Returns:
        HeadwordsExtraction: A spaCy component.
    """

    return HeadwordsExtractionComponent(
        nlp,
        name=name,
        raise_error=raise_error,
        normalize_to_entity=normalize_to_entity,
        normalize_to_noun_chunk=normalize_to_noun_chunk,
        force=force,
    )
