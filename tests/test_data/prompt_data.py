from typing import List, Tuple

from conspiracies import SpanTriplet, StringTriplet
from spacy.language import Language
from spacy.tokens import Doc

from ..utils import nlp_da  # noqa: F401

test_thread = """@user2: I was hurt.
@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough. END
"""  # noqa: E501

test_tweet = "@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough."  # noqa: E501


PromptTemplate1_expected_response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"  # noqa: E501
PromptTemplate1_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        text=test_tweet,
    ),
]

PromptTemplate2_expected_response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"  # noqa: E501
PromptTemplate2_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        text=test_tweet,
    ),
]

MarkdownPromptTemplate1_expected_response = """ This | is | a test tweet |
| | I | am commenting | on something someone else said |
| | this | is not | good enough. |
| | This | is not |"""
MarkdownPromptTemplate1_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        text=test_tweet,
    ),
]

MarkdownPromptTemplate2_expected_response = """| This | is | a test tweet |
| I | am commenting | on something someone else said |
| @user2 | this is not good enough |"""
MarkdownPromptTemplate2_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        text=test_tweet,
    ),
]

XMLStylePromptTemplate_expected_response = "@user1: user2 <subject-1>This</subject-1> <predicate-1>is</predicate-1> <object-1>a test tweet</object-1>, <subject-2>I</subject-2> <predicate-2>am commenting</predicate-2> <object-2>on something someone else said</object-2>. @user2 <subject-3>this</subject-3> <predicate-3>is not</predicate-3> <object-3>good enough.</object-3>"  # noqa: E501
XMLStylePromptTemplate_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        subject_char_span=(14, 18),
        predicate_char_span=(19, 21),
        object_char_span=(22, 34),
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        subject_char_span=(36, 37),
        predicate_char_span=(38, 51),
        object_char_span=(52, 82),
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        subject_char_span=(91, 95),
        predicate_char_span=(96, 102),
        object_char_span=(103, 115),
        text=test_tweet,
    ),
]

XMLStylePromptTemplate_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        subject_char_span=(14, 18),
        predicate_char_span=(19, 21),
        object_char_span=(22, 34),
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        subject_char_span=(36, 37),
        predicate_char_span=(38, 51),
        object_char_span=(52, 82),
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        subject_char_span=(91, 95),
        predicate_char_span=(96, 102),
        object_char_span=(103, 115),
        text=test_tweet,
    ),
]


def load_gold_triplets(
    nlp_da: Language,  # noqa: F811
) -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    # gold annotations
    doc = nlp_da(test_tweet)  # type: ignore
    span_triplets_ = [
        SpanTriplet.from_doc(t, doc=doc, nlp=nlp_da)  # type: ignore
        for t in XMLStylePromptTemplate_expected_triplets
    ]
    span_triplets = [triplet for triplet in span_triplets_ if triplet is not None]

    # copy them to test with multiple examples.
    return [doc, doc], [span_triplets, span_triplets]
