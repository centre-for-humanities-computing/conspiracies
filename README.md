
# 👁‍🗨 Conspiracies
[![python versions](https://img.shields.io/badge/Python-%3E=3.7-blue)](https://github.com/centre-for-humanities-computing/conspiracies)
[![Code style: black](https://img.shields.io/badge/Code%20Style-Black-black)](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
[![github actions pytest](https://github.com/centre-for-humanities-computing/conspiracies/actions/workflows/pytest.yml/badge.svg)](https://github.com/centre-for-humanities-computing/conspiracies/actions)
[![spacy](https://img.shields.io/badge/built%20with-spaCy-09a3d5.svg)](https://spacy.io)


<!-- [![release version](https://img.shields.io/badge/belief_graph%20Version-0.0.1-green)](https://github.com/centre-for-humanities-computing/conspiracies) -->

Discovering and examining conspiracies using NLP.



## 🔧 Installation
Installation using pip:
```bash
pip install pip --upgrade
pip install conspiracies
```

Note that this package is dependent on AllenNLP and thus does not support Windows.

## 👩‍💻 Usage

### Coreference model
A small use case of the coreference component in spaCy.

```python
import spacy
from spacy.tokens import Span
from conspiracies.coref import CoreferenceComponent 

nlp = spacy.blank("da")
nlp.add_pipe("allennlp_coref")
doc = nlp("Do you see Julie over there? She is really into programming!")

assert isinstance(doc._.coref_clusters, list)

for sent in doc.sents:
    assert isinstance(sent._.coref_cluster, list)
    assert isinstance(sent._.coref_cluster[0], tuple)
    assert isinstance(sent._.coref_cluster[0][0], int)
    assert isinstance(sent._.coref_cluster[0][1], Span)
```


<details>
  <summary>Details on output </summary>

Examining the output a bit further:

```python
print("DOC LEVEL (Coref clusters)")
print(doc._.coref_clusters)
print("-----\n\nSPAN LEVEL (sentences)")
for sent in doc.sents:
    print(sent._.coref_cluster)
print("-----\n\nSPAN LEVEL (entities)\n")
for sent in doc.sents:
    for i, coref_entity in sent._.coref_cluster:
        print(f"Coref Entity: {coref_entity} \nAntecedent: {coref_entity._.antecedent}")
        print("\n")
```

This should produce the following output

```python
DOC LEVEL (Coref clusters)
[(0, [Julie, She])]
-----

SPAN LEVEL (sentences)
[(0, Julie)]
[(0, She)]
-----

SPAN LEVEL (entities)

Coref Entity: Julie 
Antecedent: Julie


Coref Entity: She 
Antecedent: Julie
```

</details>


### Headword Extraction
A small use case of how to use the headword extraction component to extract headwords.

```python
import spacy
from conspiracies.HeadWordExtractionComponent import contains_ents

nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("heads_extraction")

doc = nlp("Mette Frederiksen is the Danish politician.")
heads_spans = []

for sent in doc:
    sent._.most_common_ancestor  # extract the most common ancestor i.e. span head
```

### Wordpiece length normalization Extraction
A small use case of how to use word piece length normalization to normalize the length of
your texts in case you are applying transformer-based pipelines.

```python
import spacy
from transformers import AutoTokenizer

# load nlp (we don't recommend a trf based spacy model as it is too slow)
nlp = spacy.load("da_core_news_lg")
# load huggingface tokenizer - should be the same as the model you wish to apply later
tokenizer_name = "DaNLP/da-bert-tone-subjective-objective"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

# An example with a very long text
from conspiracies import wordpiece_length_normalization
long_text = ["Hej mit navn er Kenneth. " * 200]
normalized_text = wordpiece_length_normalization(long_text, nlp, tokenizer, max_length=500)
assert len(norm_text) > 1, "a long text should be split into multiple texts"
```

# RelationExtraction

A Python library for extracting knowledge triplets from a text document.

## :wrench: Installation


```python

from conspiracies.relationextraction import KnowledgeTriplets


test_sents = [
    "Lasse er en dreng på 26 år.",
    "Jeg arbejder som tømrer",
    "Albert var videnskabsmand og døde i 1921",
    "Lasse lives in Denmark and owns two cats",
]


test_sents = [
    "Pernille Blume vinder delt EM-sølv i Ungarn.",
    "Pernille Blume blev nummer to ved EM på langbane i disciplinen 50 meter fri.",
    "Hurtigst var til gengæld hollænderen Ranomi Kromowidjojo, der sikrede sig guldet i tiden 23,97 sekunder.",
    "Og at formen er til en EM-sølvmedalje tegner godt, siger Pernille Blume med tanke på, at hun få uger siden var smittet med corona.",
    "Ved EM tirsdag blev det ikke til medalje for den danske medley for mixede hold i 4 x 200 meter fri.",
    "In a phone call on Monday, Mr. Biden warned Mr. Netanyahu that he could fend off criticism of the Gaza strikes for only so long, according to two people familiar with the call",
    "That phone call and others since the fighting started last week reflect Mr. Biden and Mr. Netanyahu’s complicated 40-year relationship.",
    "Politiet skal etterforske Siv Jensen etter mulig smittevernsbrudd.",
    "En av Belgiens mest framträdande virusexperter har flyttats med sin familj till skyddat boende efter hot från en beväpnad högerextremist.",
]


# initialize a class object
# call the class method for extracting triplets from a given list of sentences

relations = KnowledgeTriplets()
final_result = relations.extract_relations(test_sents)


print(final_result ["sentence"])
print(final_result ["extraction_3"])
```

## With spaCy
```py
from conspiracies.relationextraction import SpacyRelationExtractor
import spacy


nlp = spacy.load("da_core_news_sm")

test_sents = [
    "Pernille Blume vinder delt EM-sølv i Ungarn.",
    "Pernille Blume blev nummer to ved EM på langbane i disciplinen 50 meter fri.",
    "Hurtigst var til gengæld hollænderen Ranomi Kromowidjojo, der sikrede sig guldet i tiden 23,97 sekunder.",
    "Og at formen er til en EM-sølvmedalje tegner godt, siger Pernille Blume med tanke på, at hun få uger siden var smittet med corona.",
    "Ved EM tirsdag blev det ikke til medalje for den danske medley for mixede hold i 4 x 200 meter fri.",
    "In a phone call on Monday, Mr. Biden warned Mr. Netanyahu that he could fend off criticism of the Gaza strikes for only so long, according to two people familiar with the call",
    "That phone call and others since the fighting started last week reflect Mr. Biden and Mr. Netanyahu’s complicated 40-year relationship.",
    "Politiet skal etterforske Siv Jensen etter mulig smittevernsbrudd.",
    "En av Belgiens mest framträdande virusexperter har flyttats med sin familj till skyddat boende efter hot från en beväpnad högerextremist.",
]


# change these to your purposes. 2.7 is the default confidence threshold(the bulk of bad relations not kept and the majority of correct ones kept)
# batch_size should be changed according to your device. Can most likely be bumped up a fair bit
config = {"confidence_threshold": 2.7, "model_args": {"batch_size": 10}}
nlp.add_pipe("relation_extractor", config=config)

pipe = nlp.pipe(test_sents)

for d in pipe:
    print(d.text, "\n", d._.relation_triplets)

```






## FAQ

### How do I run the tests?
To run the test, you will need to install the package in editable mode. This is
intentional as it ensures that you always run the package installation before running
the tests, which ensures that the installation process works as intended.

To run the test you can use the following code:
```
# download repo
git clone https://github.com/centre-for-humanities-computing/conspiracies
cd conspiracies

# install package
pip install --editable .

# run tests
python -m  pytest
```

## Contact
Please use the [GitHub Issue Tracker](https://github.com/centre-for-humanities-computing/conspiracies/issues) to contact us on this project.
