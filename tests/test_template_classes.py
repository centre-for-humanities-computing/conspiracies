import pytest
from conspiracies import (
    PromptTemplate1,
    PromptTemplate2,
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    XMLStylePromptTemplate,
    StringTriplet,
)
from conspiracies.data import load_gold_triplets


def get_examples_task_introduction():
    docs, triplets = load_gold_triplets()
    examples = (docs[:5], triplets[:5])
    task_description = "This is a test task description"
    test_tweet = "@user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough."
    return examples, task_description, test_tweet


def test_PromptTemplate1():
    examples, task_description, test_tweet = get_examples_task_introduction()
    template = PromptTemplate1(task_description, examples)
    prompt = template.create_prompt(test_tweet)
    expected_prompt = """This is a test task description

---

Tweet: @Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.
Triplets: (@Berry1952K) (Synes) (det er total mangel på respekt)\n\t(det) (er) (total mangel på respekt)
---
Tweet: @Berry1952K: @BibsenSkyt @JakobEllemann Det er underordnet, det er almindelig anstændighed  at give mere end en dag. Hvor svært kan det lige være uanset om de har råbt op i måneder.
Triplets: (Det) (er) (underordnet)
\t(det) (er) (almindelig anstændighed  at give mere end en dag)
\t(de) (har råbt) (op)
---
Tweet: @SSTbrostrom: Jeg forstår godt mange synes nye krav om mundbind er vidtgående. Skal også selv vænne mig til nye krav skal på i butik osv. men det er altså ikke slemt. Dokumentationen har vi, og med aktuelle smittetryk i Danmark er det rettidig omhu #sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh
Triplets: (@SSTbrostrom) (forstår) (mange synes nye krav om mundbind er vidtgående)
\t(mange) (synes) (nye krav om mundbind er vidtgående)
\t(nye krav om mundbind) (er) (vidtgående)
\t(det) (er) (ikke slemt)
\t(vi) (har) (Dokumentationen)
\t(det) (er) (rettidig omhu)
---
Tweet: @Ihavequestione: @SSTbrostrom Men vi bragte da smitten ned i foråret uden mundbind, så det er underligt det nu skal indføres 🤷🏻\u200d♂️
Triplets: (vi) (bragte) (smitten ned i foråret)
\t(det) (er) (underligt det nu skal indføres)
\t(det) (skal indføres) (nu)
---
Tweet: @siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom Det første punkt under potentielle fordele er alt rigeligt til at indføre mundbindstvang overalt i det offentlige rum.
Triplets: (Det første punkt under potentielle fordele) (er) (rigeligt til at indføre mundbindstvang overalt i det offentlige rum)
---

Tweet: @user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.
Triplets:"""

    assert prompt == expected_prompt

    response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"
    extracted_triplets = template.parse_prompt(response, test_tweet)
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
    assert extracted_triplets == expected_triplets


def test_PromptTemplate2():
    examples, task_description, test_tweet = get_examples_task_introduction()
    template = PromptTemplate2(task_description, examples)
    prompt = template.create_prompt(test_tweet)
    expected_prompt = """This is a test task description

---

Tweet: @Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.

Tweet: @Berry1952K: @BibsenSkyt @JakobEllemann Det er underordnet, det er almindelig anstændighed  at give mere end en dag. Hvor svært kan det lige være uanset om de har råbt op i måneder.

Tweet: @SSTbrostrom: Jeg forstår godt mange synes nye krav om mundbind er vidtgående. Skal også selv vænne mig til nye krav skal på i butik osv. men det er altså ikke slemt. Dokumentationen har vi, og med aktuelle smittetryk i Danmark er det rettidig omhu #sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh

Tweet: @Ihavequestione: @SSTbrostrom Men vi bragte da smitten ned i foråret uden mundbind, så det er underligt det nu skal indføres 🤷🏻\u200d♂️

Tweet: @siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom Det første punkt under potentielle fordele er alt rigeligt til at indføre mundbindstvang overalt i det offentlige rum.


Triplets: (@Berry1952K) (Synes) (det er total mangel på respekt)
\t(det) (er) (total mangel på respekt)
Triplets: (Det) (er) (underordnet)
\t(det) (er) (almindelig anstændighed  at give mere end en dag)
\t(de) (har råbt) (op)
Triplets: (@SSTbrostrom) (forstår) (mange synes nye krav om mundbind er vidtgående)
\t(mange) (synes) (nye krav om mundbind er vidtgående)
\t(nye krav om mundbind) (er) (vidtgående)
\t(det) (er) (ikke slemt)
\t(vi) (har) (Dokumentationen)
\t(det) (er) (rettidig omhu)\nTriplets: (vi) (bragte) (smitten ned i foråret)
\t(det) (er) (underligt det nu skal indføres)
\t(det) (skal indføres) (nu)
Triplets: (Det første punkt under potentielle fordele) (er) (rigeligt til at indføre mundbindstvang overalt i det offentlige rum)

---

Tweet: @user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.

Triplets:"""

    assert prompt == expected_prompt

    response = "\n\n(This) (is) (a test tweet)\n(I) (am commenting)\n(this) (is not) (good enough.)"
    extracted_triplets = template.parse_prompt(response, test_tweet)
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
    assert extracted_triplets == expected_triplets


def test_MarkdownPromptTemplate1():
    examples, task_description, test_tweet = get_examples_task_introduction()
    template = MarkdownPromptTemplate1(task_description, examples)
    prompt = template.create_prompt(test_tweet)
    expected_prompt = """This is a test task description
| Tweet | Subject | Predicate | Object |
| --- | --- | --- | --- |
| @Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere. | @Berry1952K | Synes | det er total mangel på respekt |
| | det | er | total mangel på respekt |
| @Berry1952K: @BibsenSkyt @JakobEllemann Det er underordnet, det er almindelig anstændighed  at give mere end en dag. Hvor svært kan det lige være uanset om de har råbt op i måneder. | Det | er | underordnet |
| | det | er | almindelig anstændighed  at give mere end en dag |
| | de | har råbt | op |
| @SSTbrostrom: Jeg forstår godt mange synes nye krav om mundbind er vidtgående. Skal også selv vænne mig til nye krav skal på i butik osv. men det er altså ikke slemt. Dokumentationen har vi, og med aktuelle smittetryk i Danmark er det rettidig omhu #sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh | @SSTbrostrom | forstår | mange synes nye krav om mundbind er vidtgående |
| | mange | synes | nye krav om mundbind er vidtgående |
| | nye krav om mundbind | er | vidtgående |
| | det | er | ikke slemt |
| | vi | har | Dokumentationen |
| | det | er | rettidig omhu |
| @Ihavequestione: @SSTbrostrom Men vi bragte da smitten ned i foråret uden mundbind, så det er underligt det nu skal indføres 🤷🏻\u200d♂️ | vi | bragte | smitten ned i foråret |
| | det | er | underligt det nu skal indføres |
| | det | skal indføres | nu |
| @siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom Det første punkt under potentielle fordele er alt rigeligt til at indføre mundbindstvang overalt i det offentlige rum. | Det første punkt under potentielle fordele | er | rigeligt til at indføre mundbindstvang overalt i det offentlige rum |
| @user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough. |"""

    assert prompt == expected_prompt

    response = """ This | is | a test tweet |
| | I | am commenting | on something someone else said |
| | this | is not | good enough. |
| | This | is not |"""
    extracted_triplets = template.parse_prompt(response, test_tweet)
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
    assert extracted_triplets == expected_triplets


def test_MarkdownPromptTemplate2():
    examples, task_description, test_tweet = get_examples_task_introduction()
    template = MarkdownPromptTemplate2(task_description, examples)
    prompt = template.create_prompt(test_tweet)
    expected_prompt = """This is a test task description

@Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.

| Subject | Predicate | Object |
| --- | --- | --- |
| @Berry1952K | Synes | det er total mangel på respekt |
| det | er | total mangel på respekt |

@Berry1952K: @BibsenSkyt @JakobEllemann Det er underordnet, det er almindelig anstændighed  at give mere end en dag. Hvor svært kan det lige være uanset om de har råbt op i måneder.

| Subject | Predicate | Object |
| --- | --- | --- |
| Det | er | underordnet |
| det | er | almindelig anstændighed  at give mere end en dag |
| de | har råbt | op |

@SSTbrostrom: Jeg forstår godt mange synes nye krav om mundbind er vidtgående. Skal også selv vænne mig til nye krav skal på i butik osv. men det er altså ikke slemt. Dokumentationen har vi, og med aktuelle smittetryk i Danmark er det rettidig omhu #sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh

| Subject | Predicate | Object |
| --- | --- | --- |
| @SSTbrostrom | forstår | mange synes nye krav om mundbind er vidtgående |
| mange | synes | nye krav om mundbind er vidtgående |
| nye krav om mundbind | er | vidtgående |
| det | er | ikke slemt |
| vi | har | Dokumentationen |
| det | er | rettidig omhu |

@Ihavequestione: @SSTbrostrom Men vi bragte da smitten ned i foråret uden mundbind, så det er underligt det nu skal indføres 🤷🏻\u200d♂️

| Subject | Predicate | Object |
| --- | --- | --- |
| vi | bragte | smitten ned i foråret |
| det | er | underligt det nu skal indføres |
| det | skal indføres | nu |

@siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom Det første punkt under potentielle fordele er alt rigeligt til at indføre mundbindstvang overalt i det offentlige rum.

| Subject | Predicate | Object |
| --- | --- | --- |
| Det første punkt under potentielle fordele | er | rigeligt til at indføre mundbindstvang overalt i det offentlige rum |

@user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.

| Subject | Predicate | Object |
| --- | --- | --- |
"""

    assert prompt == expected_prompt

    response = """| This | is | a test tweet |
| I | am commenting | on something someone else said |
| @user2 | this is not good enough |"""
    extracted_triplets = template.parse_prompt(response, test_tweet)
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
    assert extracted_triplets == expected_triplets


def test_XMLStylePromptTemplate():
    examples, task_description, test_tweet = get_examples_task_introduction()
    template = XMLStylePromptTemplate(task_description, examples)
    prompt = template.create_prompt(test_tweet)
    expected_prompt = """This is a test task description

@Berry1952K: @BibsenSkyt @JakobEllemann Synes det er total mangel på respekt for alle andre partiledere.
<subject-1>@Berry1952K</subject-1>: @BibsenSkyt @JakobEllemann <predicate-1>Synes </predicate-1><object-1><subject-2>det </subject-2><predicate-2>er </predicate-2><object-2>total mangel på respekt </object-1></object-2>for alle andre partiledere.

@Berry1952K: @BibsenSkyt @JakobEllemann Det er underordnet, det er almindelig anstændighed  at give mere end en dag. Hvor svært kan det lige være uanset om de har råbt op i måneder.
@Berry1952K: @BibsenSkyt @JakobEllemann <subject-1>Det </subject-1><predicate-1>er </predicate-1><object-1>underordnet</object-1>, <subject-2>det </subject-2><predicate-2>er </predicate-2><object-2>almindelig anstændighed  at give mere end en dag</object-2>. Hvor svært kan det lige være uanset om <subject-3>de </subject-3><predicate-3>har råbt </predicate-3><object-3>op </object-3>i måneder.

@SSTbrostrom: Jeg forstår godt mange synes nye krav om mundbind er vidtgående. Skal også selv vænne mig til nye krav skal på i butik osv. men det er altså ikke slemt. Dokumentationen har vi, og med aktuelle smittetryk i Danmark er det rettidig omhu #sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh
<subject-1>@SSTbrostrom</subject-1>: Jeg <predicate-1>forstår </predicate-1>godt <object-1><subject-2>mange </subject-2><predicate-2>synes </predicate-2><object-2><subject-3>nye krav om mundbind </subject-3><predicate-3>er </predicate-3><object-3>vidtgående</object-1></object-2></object-3>. Skal også selv vænne mig til nye krav skal på i butik osv. men <subject-4>det </subject-4><predicate-4>er </predicate-4>altså <object-4>ikke slemt</object-4>. <object-5>Dokumentationen </object-5><predicate-5>har </predicate-5><subject-5>vi</subject-5>, og med aktuelle smittetryk i Danmark <predicate-6>er </predicate-6><subject-6>det </subject-6><object-6>rettidig omhu </object-6>#sundpol #SundhedForAlle  https://t.co/SlmGZtN5dh

@Ihavequestione: @SSTbrostrom Men vi bragte da smitten ned i foråret uden mundbind, så det er underligt det nu skal indføres 🤷🏻\u200d♂️
@Ihavequestione: @SSTbrostrom Men <subject-1>vi </subject-1><predicate-1>bragte </predicate-1>da <object-1>smitten ned i foråret </object-1>uden mundbind, så <subject-2>det </subject-2><predicate-2>er </predicate-2><object-2>underligt <subject-3>det </subject-3><object-3>nu </object-3><predicate-3>skal indføres </object-2></predicate-3>🤷🏻\u200d♂️

@siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom Det første punkt under potentielle fordele er alt rigeligt til at indføre mundbindstvang overalt i det offentlige rum.
@siggithilde: @Ihavequestione @svogdrup @GianniRivera69 @SSTbrostrom <subject-1>Det første punkt under potentielle fordele </subject-1><predicate-1>er </predicate-1>alt <object-1>rigeligt til at indføre mundbindstvang overalt i det offentlige rum</object-1>.

@user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough.
"""

    assert prompt == expected_prompt

    response = "@user1: <subject-1>This</subject-1> <predicate-1>is</predicate-1> <object-1>a test tweet</object-1>, <subject-2>I</subject-2> <predicate-2>am commenting</predicate-2> <object-2>on something someone else said</object-2>. @user2 <subject-3>this</subject-3> <predicate-3>is not</predicate-3> <object-3>good enough.</object-3>"
    extracted_triplets = template.parse_prompt(response, test_tweet)
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
    assert extracted_triplets == expected_triplets
