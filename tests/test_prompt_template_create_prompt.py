import pytest

from conspiracies import (
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    PromptTemplate1,
    PromptTemplate2,
    XMLStylePromptTemplate,
)

from .test_data.prompt_data import load_gold_triplets, test_tweet


def get_examples_task_introduction():
    examples = load_gold_triplets()
    task_description = "This is a test task description"
    return examples, task_description, test_tweet


PromptTemplate1_expected_prompt = """This is a test task description

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
Triplets:"""  # noqa: E501

PromptTemplate2_expected_prompt = """This is a test task description

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

Triplets:"""  # noqa: E501

MarkdownPromptTemplate1_expected_prompt = """This is a test task description
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
| @user1: This is a test tweet, I am commenting on something someone else said. @user2 this is not good enough. |"""  # noqa: E501

MarkdownPromptTemplate2_expected_prompt = """This is a test task description

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
"""  # noqa: E501

XMLStylePromptTemplate_expected_prompt = """This is a test task description

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
"""  # noqa: E501


examples, task_description, test_tweet = get_examples_task_introduction()  # noqa


@pytest.mark.parametrize(
    "template, target, examples, task_description, expected_prompt",
    [
        (
            PromptTemplate1,
            test_tweet,
            examples,
            task_description,
            PromptTemplate1_expected_prompt,
        ),
        (
            PromptTemplate2,
            test_tweet,
            examples,
            task_description,
            PromptTemplate2_expected_prompt,
        ),
        (
            MarkdownPromptTemplate1,
            test_tweet,
            examples,
            task_description,
            MarkdownPromptTemplate1_expected_prompt,
        ),
        (
            MarkdownPromptTemplate2,
            test_tweet,
            examples,
            task_description,
            MarkdownPromptTemplate2_expected_prompt,
        ),
        (
            XMLStylePromptTemplate,
            test_tweet,
            examples,
            task_description,
            XMLStylePromptTemplate_expected_prompt,
        ),
    ],
)
def test_PromptTemplate_create_prompt(
    template,
    target,
    examples,
    task_description,
    expected_prompt,
):
    template = template(task_description, examples)
    prompt = template.create_prompt(target)
    assert prompt == expected_prompt
