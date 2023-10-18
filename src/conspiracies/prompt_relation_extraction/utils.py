from typing import List

from catalogue import registry
from spacy.tokens import Doc, Span


@registry.split_doc_functions.register("conspiracies/split_thread_to_tweets")
def split_thread_to_tweets(doc: Doc) -> List[Span]:
    """Split a thread into tweets.

    Args:
        doc (Doc): A spaCy Doc object.

    Returns:
        List[Doc]: A list of spaCy Doc objects, each representing a tweet.
    """
    # split doc by newline
    tweets = []

    start = 0
    end = 0
    for token in doc:
        if token.text == "\n":  # TODO: check that this actually splits the thread
            end = token.i
            tweets.append(doc[start:end])
            start = end + 1
            tweets.append(doc[start:])
    return tweets
