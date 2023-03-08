import pytest
from conspiracies import (
    PromptTemplate1,
    PromptTemplate2,
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    XMLStylePromptTemplate,
    StringTriplet,
)


def get_response_and_expected_triplets(template, test_tweet):
    if isinstance(template, PromptTemplate1):
        response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"  # noqa: E501
        expected_triplets = [
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
    elif isinstance(template, PromptTemplate2):
        response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"  # noqa: E501
        expected_triplets = [
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
    elif isinstance(template, MarkdownPromptTemplate1):
        response = """ This | is | a test tweet |
| | I | am commenting | on something someone else said |
| | this | is not | good enough. |
| | This | is not |"""
        expected_triplets = [
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
    elif isinstance(template, MarkdownPromptTemplate2):
        response = """| This | is | a test tweet |
| I | am commenting | on something someone else said |
| @user2 | this is not good enough |"""
        expected_triplets = [
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
    elif isinstance(template, XMLStylePromptTemplate):
        response = "@user1: <subject-1>This</subject-1> <predicate-1>is</predicate-1> <object-1>a test tweet</object-1>, <subject-2>I</subject-2> <predicate-2>am commenting</predicate-2> <object-2>on something someone else said</object-2>. @user2 <subject-3>this</subject-3> <predicate-3>is not</predicate-3> <object-3>good enough.</object-3>"  # noqa: E501
        expected_triplets = [
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
    return response, expected_triplets


test_tweet = "@user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough."  # noqa: E501


@pytest.mark.parametrize(
    "template, target",
    [
        (PromptTemplate1, test_tweet),
        (PromptTemplate2, test_tweet),
        (MarkdownPromptTemplate1, test_tweet),
        (MarkdownPromptTemplate2, test_tweet),
        (XMLStylePromptTemplate, test_tweet),
    ],
)
def test_PromptTemplate_parse_prompt(template, target):
    template_instance = template()
    response, expected_triplets = get_response_and_expected_triplets(
        template_instance,
        target,
    )
    parsed_triplets = template_instance.parse_prompt(response, target)
    assert parsed_triplets == expected_triplets
