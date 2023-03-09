import pytest
from conspiracies import (
    PromptTemplate1,
    PromptTemplate2,
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    XMLStylePromptTemplate,
    StringTriplet,
)

test_tweet = "@user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough."  # noqa: E501

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

XMLStylePromptTemplate_expected_response = "@user1: <subject-1>This</subject-1> <predicate-1>is</predicate-1> <object-1>a test tweet</object-1>, <subject-2>I</subject-2> <predicate-2>am commenting</predicate-2> <object-2>on something someone else said</object-2>. @user2 <subject-3>this</subject-3> <predicate-3>is not</predicate-3> <object-3>good enough.</object-3>"  # noqa: E501
XMLStylePromptTemplate_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        subject_char_span=(8, 12),
        predicate_char_span=(13, 15),
        object_char_span=(16, 28),
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        subject_char_span=(30, 31),
        predicate_char_span=(32, 45),
        object_char_span=(46, 76),
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        subject_char_span=(85, 89),
        predicate_char_span=(90, 96),
        object_char_span=(97, 109),
        text=test_tweet,
    ),
]


@pytest.mark.parametrize(
    "template, target, response, expected_triplets",
    [
        (
            PromptTemplate1,
            test_tweet,
            PromptTemplate1_expected_response,
            PromptTemplate1_expected_triplets,
        ),
        (
            PromptTemplate2,
            test_tweet,
            PromptTemplate2_expected_response,
            PromptTemplate2_expected_triplets,
        ),
        (
            MarkdownPromptTemplate1,
            test_tweet,
            MarkdownPromptTemplate1_expected_response,
            MarkdownPromptTemplate1_expected_triplets,
        ),
        (
            MarkdownPromptTemplate2,
            test_tweet,
            MarkdownPromptTemplate2_expected_response,
            MarkdownPromptTemplate2_expected_triplets,
        ),
        (
            XMLStylePromptTemplate,
            test_tweet,
            XMLStylePromptTemplate_expected_response,
            XMLStylePromptTemplate_expected_triplets,
        ),
    ],
)
def test_PromptTemplate_parse_prompt(template, target, response, expected_triplets):
    template_instance = template()
    parsed_triplets = template_instance.parse_prompt(response, target)
    assert parsed_triplets == expected_triplets
