# Fetch tweet

## Guide to run `create_context_threads.py`

Use the _tweet threads_ branch [conspiracies repo](https://github.com/centre-for-humanities-computing/conspiracies/tree/twitter-threads).




## Flags

| Flag           | Description |Default |
| ------------- |:-------------|:-------------|
| `-s`          | start date of the period of tweets (format: `"YYYY-MM-DD"`)     |`-s "2019-05-22"`   | 
| `-e`      | days from the start date to include in the extraction, e.g. 15       |`-e 15`   |
| `-p`      | Files to glob for tweets in grundvig dir: `/data/004_twitter-stopword/`. <br /> Use "*.ndjson" to look through tweets with the defined dates in __all__ the files. <br /> (Notice, to save time, choose the files with the relevant time period in filename that includes the wanted dates and use __"part?"__ to include parts 1, 2, and 3, e.g. `"da_stopwords_part?_2019-01-01_2020-12-31.ndjson"`)     | `-p "da_stopwords_part?_2019-01-01_2020-12-31.ndjson"`   |
| `-c`      | Number of tweets to include in context length.     | `-c 4`   |

## Run

```
python paper/src/create_context_threads.py

# Example
python paper/src/create_context_threads.py -s "2019-05-22" -e 15 -p "da_stopwords_part?_2019-01-01_2020-12-31.ndjson" -c 4

```

### Output: 
* This will output an ndjson file where every newline is `List[Dict[str, Any]]` ~ a list with context tweet and the last one being the tweet that the context tweets relates to
*

If any questions should come up, feel free to contact Sara or Thea at CHCAA.