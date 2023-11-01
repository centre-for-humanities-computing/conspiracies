from typing import List

import spacy

from conspiracies.docprocessing.relationextraction.data_classes import (
    install_extensions,
)
from conspiracies.docprocessing.relationextraction.gptprompting import (
    DocTriplets,
    SpanTriplet,
    StringTriplet,
)
from spacy.tokens import Doc

test_thread = """@user2: I was hurt. END
@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough. END
"""  # noqa: E501

test_tweet = "@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough."  # noqa: E501

### For testing prompt parsing ###

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

XMLStylePromptTemplate_expected_response = "@user1: @user2 <subject-1>This</subject-1> <predicate-1>is</predicate-1> <object-1>a test tweet</object-1>, <subject-2>I</subject-2> <predicate-2>am commenting</predicate-2> <object-2>on something someone else said</object-2>. @user2 <subject-3>this</subject-3> <predicate-3>is not</predicate-3> <object-3>good enough.</object-3>"  # noqa: E501

XMLStylePromptTemplate_expected_triplets = [
    StringTriplet(
        subject="This",
        predicate="is",
        object="a test tweet",
        subject_char_span=(15, 19),
        predicate_char_span=(20, 22),
        object_char_span=(23, 35),
        text=test_tweet,
    ),
    StringTriplet(
        subject="I",
        predicate="am commenting",
        object="on something someone else said",
        subject_char_span=(37, 38),
        predicate_char_span=(39, 52),
        object_char_span=(53, 83),
        text=test_tweet,
    ),
    StringTriplet(
        subject="this",
        predicate="is not",
        object="good enough.",
        subject_char_span=(92, 96),
        predicate_char_span=(97, 103),
        object_char_span=(104, 116),
        text=test_tweet,
    ),
]

chatGPTPromptTemplate_expected_response = """I extracted the following triplets:
	@user1 - commenting on - something someone else said
	@user2 - this is - not good enough. 
Note that the verb phrase "commenting on" includes the particles "on" and "something else"."""  # noqa: E501

chatGPTPromptTemplate_expected_triplets = [
    StringTriplet(
        subject="@user1",
        predicate="commenting on",
        object="something someone else said",
        text=test_tweet,
    ),
    StringTriplet(
        subject="@user2",
        predicate="this is",
        object="not good enough.",
        text=test_tweet,
    ),
]


def load_gold_triplets() -> List[Doc]:
    """Load two examples of docs with gold annotations in the.

    ._.relation_triplets attribute.
    """
    nlp = spacy.blank("da")
    nlp.add_pipe("sentencizer")
    # gold annotations
    doc = nlp(test_tweet)  # type: ignore

    span_triplets_ = [
        SpanTriplet.from_doc(t, doc=doc, nlp=nlp)  # type: ignore
        for t in XMLStylePromptTemplate_expected_triplets
    ]
    span_triplets = [triplet for triplet in span_triplets_ if triplet is not None]

    if not Doc.has_extension("relation_triplets"):
        install_extensions()
    doc._.relation_triplets = DocTriplets(span_triplets=span_triplets, doc=doc)

    # copy them to test with multiple examples.
    return [doc, doc]


### For testing prompt creation ###

example_tweet_1 = "@Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger."  # noqa: E501
example_tweet_2 = "@minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1."  # noqa: E501
example_tweet_3 = "@almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved."  # noqa: E501
example_tweet_4 = """@fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt."""  # noqa: E501
example_tweet_5 = "@minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret."  # noqa: E501

example_triplets_1 = [
    ["@Politician1", "er uenig", "i det I siger"],
    ["@Politician1", "forlanger", "almindelig sund fornuft"],
]
example_triplets_2 = [
    ["@minister", "skriver", "en kort kommentar"],
    ["en kort kommentar", "skyder", "med skarpt"],
]
example_triplets_3 = [
    ["At blande sig", "er ikke", "en god idé"],
    ["det", "er", "bedre at holde sig for sig selv"],
    ["det", "er", "der er ikke noget at gøre ved"],
]
example_triplets_4 = [
    ["@fagperson", "vil", "gerne understrege"],
    ["mine inputs", "burde fylde", "mere"],
    ["det", "er vigtigt", "at lytte til hvad @fagperson siger"],
    ["myndighedspersoner", "burde vægte", "sådanne faglige indspark ekstra højt"],
]
example_triplets_5 = [
    ["@minister", "lytter", "til @fagperson og @almindelig123"],
    ["@minister", "er enig", "med dem"],
    ["Solid argumentation", "har overbevist", "mig om at flertallet nok har ret"],
]


def load_examples() -> List[Doc]:
    """Load five examples of docs with gold triplet annotations.

    The examples are made up mock tweets.
    """
    nlp = spacy.blank("da")
    nlp.add_pipe("sentencizer")

    if not Doc.has_extension("relation_triplets"):
        install_extensions(force=True)
    examples: List[Doc] = []
    for example, triplet_list in [
        (example_tweet_1, example_triplets_1),
        (example_tweet_2, example_triplets_2),
        (example_tweet_3, example_triplets_3),
        (example_tweet_4, example_triplets_4),
        (example_tweet_5, example_triplets_5),
    ]:
        doc = nlp(example)
        examples.append(doc)
        span_triplets_ = [
            SpanTriplet.from_doc(t, doc=doc, nlp=nlp)  # type: ignore
            for t in triplet_list
        ]
        span_triplets = [triplet for triplet in span_triplets_ if triplet is not None]
        doc._.relation_triplets = span_triplets
    return examples


PromptTemplate1_expected_prompt = """This is a test task description

---

Tweet: @Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger.
Triplets: (@Politician1) (er uenig) (i det I siger)
\t(@Politician1) (forlanger) (Almindelig sund fornuft)
---
Tweet: @minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1.
Triplets: (@minister) (skriver) (en kort kommentar)
\t(en kort kommentar) (skyder) (med skarpt)
---
Tweet: @almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved.
Triplets: (At blande sig) (er ikke) (en god idé)
\t(det) (er) (bedre at holde sig for sig selv)
---
Tweet: @fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt.
Triplets: (@fagperson) (vil) (gerne understrege)
\t(mine inputs) (burde fylde) (mere)
\t(Det) (er vigtigt) (at lytte til hvad @fagperson siger)
\t(myndighedspersoner) (burde vægte) (sådanne faglige indspark ekstra højt)
---
Tweet: @minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret.
Triplets: (@minister) (lytter) (til @fagperson og @almindelig123)
\t(@minister) (er enig) (med dem)
\t(Solid argumentation) (har overbevist) (mig om at flertallet nok har ret)
---

Tweet: @user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.
Triplets:"""  # noqa: E501

PromptTemplate2_expected_prompt = """This is a test task description

---

Tweet: @Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger.

Tweet: @minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1.

Tweet: @almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved.

Tweet: @fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt.

Tweet: @minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret.


Triplets: (@Politician1) (er uenig) (i det I siger)
\t(@Politician1) (forlanger) (Almindelig sund fornuft)
Triplets: (@minister) (skriver) (en kort kommentar)
\t(en kort kommentar) (skyder) (med skarpt)
Triplets: (At blande sig) (er ikke) (en god idé)
\t(det) (er) (bedre at holde sig for sig selv)
Triplets: (@fagperson) (vil) (gerne understrege)
\t(mine inputs) (burde fylde) (mere)
\t(Det) (er vigtigt) (at lytte til hvad @fagperson siger)
\t(myndighedspersoner) (burde vægte) (sådanne faglige indspark ekstra højt)
Triplets: (@minister) (lytter) (til @fagperson og @almindelig123)
\t(@minister) (er enig) (med dem)
\t(Solid argumentation) (har overbevist) (mig om at flertallet nok har ret)

---

Tweet: @user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.

Triplets:"""  # noqa: E501

MarkdownPromptTemplate1_expected_prompt = """This is a test task description
| Tweet | Subject | Predicate | Object |
| --- | --- | --- | --- |
| @Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger. | @Politician1 | er uenig | i det I siger |
| | @Politician1 | forlanger | Almindelig sund fornuft |
| @minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1. | @minister | skriver | en kort kommentar |
| | en kort kommentar | skyder | med skarpt |
| @almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved. | At blande sig | er ikke | en god idé |
| | det | er | bedre at holde sig for sig selv |
| @fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt. | @fagperson | vil | gerne understrege |
| | mine inputs | burde fylde | mere |
| | Det | er vigtigt | at lytte til hvad @fagperson siger |
| | myndighedspersoner | burde vægte | sådanne faglige indspark ekstra højt |
| @minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret. | @minister | lytter | til @fagperson og @almindelig123 |
| | @minister | er enig | med dem |
| | Solid argumentation | har overbevist | mig om at flertallet nok har ret |
| @user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough. |"""  # noqa: E501

MarkdownPromptTemplate2_expected_prompt = """This is a test task description

@Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger.

| Subject | Predicate | Object |
| --- | --- | --- |
| @Politician1 | er uenig | i det I siger |
| @Politician1 | forlanger | Almindelig sund fornuft |

@minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1.

| Subject | Predicate | Object |
| --- | --- | --- |
| @minister | skriver | en kort kommentar |
| en kort kommentar | skyder | med skarpt |

@almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved.

| Subject | Predicate | Object |
| --- | --- | --- |
| At blande sig | er ikke | en god idé |
| det | er | bedre at holde sig for sig selv |

@fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt.

| Subject | Predicate | Object |
| --- | --- | --- |
| @fagperson | vil | gerne understrege |
| mine inputs | burde fylde | mere |
| Det | er vigtigt | at lytte til hvad @fagperson siger |
| myndighedspersoner | burde vægte | sådanne faglige indspark ekstra højt |

@minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret.

| Subject | Predicate | Object |
| --- | --- | --- |
| @minister | lytter | til @fagperson og @almindelig123 |
| @minister | er enig | med dem |
| Solid argumentation | har overbevist | mig om at flertallet nok har ret |

@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.

| Subject | Predicate | Object |
| --- | --- | --- |
"""  # noqa: E501

XMLStylePromptTemplate_expected_prompt = """This is a test task description

@Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger.
@Politician1: @minister @journalist <subject-1>@Politician1 </subject-1><predicate-1>er uenig </predicate-1><object-1>i det I siger</object-1>. Man kan ikke bare gøre hvad der passer en. <object-2>Almindelig sund fornuft </object-2>er det eneste <subject-2>@Politician1 </subject-2><predicate-2>forlanger</predicate-2>.

@minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1.
@minister: <subject-1>@minister </subject-1><predicate-1>skriver </predicate-1>her <object-1>en kort kommentar </object-1><subject-2>en kort kommentar </subject-2><predicate-2>skyder </predicate-2><object-2>med skarpt </object-2>på @Politician1.

@almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved.
@almindelig123: <subject-1>At blande sig </subject-1>i debatten <predicate-1>er ikke </predicate-1><object-1>en god idé</object-1>. Nogle gange <predicate-2>er </predicate-2><subject-2>det </subject-2><object-2>bedre at holde sig for sig selv</object-2>. Men sådan er det, det er der ikke noget at gøre ved.

@fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. 
Det er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt.
<subject-1>@fagperson</subject-1>: @Politician1 @minister @journalist Som fagperson <predicate-1>vil </predicate-1>@fagperson <object-1>gerne understrege </object-1>at <subject-2>mine inputs </subject-2><predicate-2>burde fylde </predicate-2><object-2>mere</object-2>. 
<subject-3>Det </subject-3><predicate-3>er vigtigt </predicate-3><object-3>at lytte til hvad @fagperson siger</object-3>, og I er alle <subject-4>myndighedspersoner </subject-4>der <predicate-4>burde vægte </predicate-4><object-4>sådanne faglige indspark ekstra højt</object-4>.

@minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret.
@minister: <subject-1>@minister </subject-1><predicate-1>lytter </predicate-1><object-1>til @fagperson og @almindelig123</object-1>. <subject-2>@minister </subject-2><predicate-2>er enig </predicate-2><object-2>med dem</object-2>. <subject-3>Solid argumentation </subject-3><predicate-3>har overbevist </predicate-3><object-3>mig om at flertallet nok har ret</object-3>.

@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.
"""  # noqa: E501


chatGPTPromptTemplate_expected_prompt = [
    {
        "role": "system",
        "content": "You are a helpful assistant who is also an expert linguist. ",
    },
    {"role": "user", "content": "Hi, I need your help on a linguistic question."},
    {"role": "assistant", "content": "Sure, what is the task?"},
    {
        "role": "user",
        "content": "This is a test task description",
    },
    {
        "role": "assistant",
        "content": "That sounds like something I can help you with. \
Let me try the first example!",
    },
    {
        "role": "user",
        "content": "The tweet is:\n@Politician1: @minister @journalist @Politician1 er uenig i det I siger. Man kan ikke bare gøre hvad der passer en. Almindelig sund fornuft er det eneste @Politician1 forlanger.\n",  # noqa: E501
    },
    {
        "role": "assistant",
        "content": "I extracted the following triplets:\n\t@Politician1 - er uenig - i det I siger\n\t@Politician1 - forlanger - Almindelig sund fornuft\n",  # noqa: E501
    },
    {
        "role": "user",
        "content": "Correct! The next tweet is:\n@minister: @minister skriver her en kort kommentar en kort kommentar skyder med skarpt på @Politician1.\n",  # noqa: E501
    },
    {
        "role": "assistant",
        "content": "I extracted the following triplets:\n\t@minister - skriver - en kort kommentar\n\ten kort kommentar - skyder - med skarpt\n",  # noqa: E501
    },
    {
        "role": "user",
        "content": "Correct! The next tweet is:\n@almindelig123: At blande sig i debatten er ikke en god idé. Nogle gange er det bedre at holde sig for sig selv. Men sådan er det, det er der ikke noget at gøre ved.\n",  # noqa: E501
    },
    {
        "role": "assistant",
        "content": "I extracted the following triplets:\n\tAt blande sig - er ikke - en god idé\n\tdet - er - bedre at holde sig for sig selv\n",  # noqa: E501
    },
    {
        "role": "user",
        "content": "Correct! The next tweet is:\n@fagperson: @Politician1 @minister @journalist Som fagperson vil @fagperson gerne understrege at mine inputs burde fylde mere. \nDet er vigtigt at lytte til hvad @fagperson siger, og I er alle myndighedspersoner der burde vægte sådanne faglige indspark ekstra højt.\n",  # noqa: E501
    },
    {
        "role": "assistant",
        "content": "I extracted the following triplets:\n\t@fagperson - vil - gerne understrege\n\tmine inputs - burde fylde - mere\n\tDet - er vigtigt - at lytte til hvad @fagperson siger\n\tmyndighedspersoner - burde vægte - sådanne faglige indspark ekstra højt\n",  # noqa: E501
    },
    {
        "role": "user",
        "content": "Correct! The next tweet is:\n@minister: @minister lytter til @fagperson og @almindelig123. @minister er enig med dem. Solid argumentation har overbevist mig om at flertallet nok har ret.\n",  # noqa: E501
    },
    {
        "role": "assistant",
        "content": "I extracted the following triplets:\n\t@minister - lytter - til @fagperson og @almindelig123\n\t@minister - er enig - med dem\n\tSolid argumentation - har overbevist - mig om at flertallet nok har ret\n",  # noqa: E501
    },
    {
        "role": "user",
        "content": "The tweet is:\n@user1: @user2 This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.\n",  # noqa: E501
    },
]
