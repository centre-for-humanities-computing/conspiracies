# Triplets-Extraction-GPT

For extraction of relational triplets using OpenAI's GPT.

## Project organization 
```
├── README.md       
├── src
│   ├── create_templates.py     <- prompt templates
│   ├── extract.py              <- extracting examples 
│   └── extract_triplets.py     <- extracting triplets using prompts
└── requirements.py
 
```

### Data
Data related to the prompts are on ucloud in ``data/triplet-extraction-gpt/``

```
├── triplet-extraction-gpt 
│   ├── predictions
│   │   └── ...                 <- .json files with output from gpt
│   ├── tagged  
│   │   ├── relations.txt 
│   │   ├── resolved_coref1.json                 
│   │   └── tagged_tweets_with_features.json
```

## Extract triplets
To extract the triplets run 
```
pip install -r requirements.txt
python src/extract_triplets.py
```
Examples and outputs will be stored in ``data/triplet-extraction-gpt/tagged/``

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

