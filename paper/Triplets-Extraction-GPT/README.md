# Triplets-Extraction-GPT
For extraction of relational triplets using OpenAI's GPT.

## Project organization

```
├── README.md      
├── src
│   ├── create_templates.py            <- prompt templates
│   ├── extract.py                     <- extracting examples
│   ├── extract_triplets.py            <- extracting triplets using prompts
│   ├── print_gpt_output.py            <- print output from one or several prompts in MD format
│   ├── save_output_comparison_json.py <- saves target tweet and extracted triplets as lists to a json file
│   └── utils.py                       <- helper functions for the other scripts
├── requirements.txt
└── validation_metrics.md              <- notes on the metrics for comparing prompt performance
```

### Data
Data related to the prompts are on ucloud in ``data/triplet-extraction-gpt/`` and on grundtvig in ``/data/conspiracies/triplet-extraction-gpt``. Scripts work for ucloud if two folders are mounted simultaneously: the data folder ``conspiracies`` in the ``pandemic-info-resp``-folder and the cloned github repository ``conspiracies`` from the ``centre-for-humanities-computing`` Github.

```
├── triplet-extraction-gpt
│   ├── predictions
│   │   └── ...                               <- .json files with output from gpt
│   ├── tagged  
│   │   ├── relations.txt
│   │   ├── resolved_coref1.json                
│   │   └── tagged_tweets_with_features.json  <- .json file with the tagget example tweets (w and w/o resolved coref)
```

## Extract triplets

To extract the triplets run

```
pip install -r requirements.txt
python src/extract_triplets.py -m ucloud/grundtvig -t 3 4

```
The flag ```-m``` tells which machine you are working on, takes values ``ucloud`` or ``grundtvig``.
The flag ``-t`` indicates templates to use. Several templates can be entered if separated by a space.
Additionally, fhe flag ``-i`` can be used to indicate number of iterations of example extraction and prompting (defaults to 2), and `-n` can be used to indicate number of tweets to use as examples. `-n` defaults to 20, which is close to the maximum number of tweets that will be allowed for the prompt string. The script checks for long prompts and decreases the number of example tweets if necessary. The remaining tweets that are tagged are used as target tweets (which right now therefore defaults to 10, since we have 30 tagged examples).
Examples and outputs (predictions) will be stored in ``data/triplet-extraction-gpt/predictions/`` or ``data/predictions/``, depending on whether you work on ucloud or grundtvig.
The following templates have been used as prompts.
<details>

<summary>Template 1</summary>

```
    {Task description}:
    ---
    Tweet: {tweet1}
    Triplet: {triplets1}
    ---
    ...
    ---
    Tweet: {tweetN}
    Triplet: {tripletsN}
    ---
    Tweet: {target_tweet}
    Triplet:
```

</details>

<details>

<summary>Template 2</summary>

```
    {Task description}:

    ---
    Tweet: {tweet1}
    Tweet: {tweet2}
    ...
    Tweet: {tweetN}
    Triplet: {triplets1}
    Triplet: {triplets2}
    ...
    Triplet: {tripletsN}
    ---
    Tweet: {target_tweet}
    Triplet:
```
</details>

<details>
<summary>Template 3</summary>

```
    {Task description}

    | Tweet | Subject | Predicate | Object |
    | --- | --- | --- | --- |
    | {tweet 1} | {subject 1} | {predicate 1} | {object 1} |
    | {tweet 1} | {subject 2} | {predicate 2} | {object 2} |

    ...

    | {tweet n} | {subject 1} | {predicate 1} | {object 1} |
    | {tweet n} | {subject 2} | {predicate 2} | {object 2} |
    | {target_tweet} |
```
</details>

<details>
<summary>Template 4</summary>

```
    {Task description}

    {tweet 1}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |
    | {triplet 1 from tweet 1}
    | {triplet 2 from tweet 1}

    {tweet 2}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |
    | {triplet 1 from tweet 2}
    | {triplet 2 from tweet 2}
    ...

    {target tweet}

    | Subject | Predicate | Object |
    | ---- | ---- | ---- |

```

</details>


## Print the output from GPT

The output (predictions) from the GPT model can be printed in a markdown friendly fashion that also prints the manually tagged version.
To generate output that compares one or several prompts to the tagged gold standard run
```
python src/print_gpt_output.py -m ucloud/grundtvig -t 3 4
```
The flag ```-m``` tells which machine you are working on, takes values ``ucloud`` or ``grundtvig``.
The flag ``-t`` indicates templates to use. Several templates can be entered if separated by a space. Additionally, fhe flag ``-i`` can be used to indicate number of iterations of example extraction and prompting (defaults to 2). To print output from all gpt predictions, set ``-i`` equal to the ``-i`` used when extracting the triplets.


## Save extracted triplets as lists
The triplets extracted by GPT can be saved to a json file. The file will contain a list of dicts with the target tweet, the gold tagged triplets and the triplets extracted by GPT. 
To generate the file with the triplets as lists, run
```
python src/save_output_comparison_json.py -m ucloud/grundtvig -t 3 4
```
The flag ```-m``` tells which machine you are working on, takes values ``ucloud`` or ``grundtvig``.
The flag ``-t`` indicates templates to use. Several templates can be entered if separated by a space. Additionally, fhe flag ``-i`` can be used to indicate number of iterations of example extraction and prompting (defaults to 2). To print output from all gpt predictions, set ``-i`` equal to the ``-i`` used when extracting the triplets.
The flag ``-s`` indicated whether or not to run a sanity check on triplets before saving (e.g. removing triplets with not exactly three elements). Default to True