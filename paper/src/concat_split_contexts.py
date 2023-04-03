"""Functions for concatenating and splitting tweets and their context tweets
for coreference resolution."""
from typing import List
import ndjson
from glob import glob


def ndjson_gen(filepath: str):
    """Creates a generator for ndjson files and yields the tweets."""
    for file in glob(filepath):
        with open(file) as f:
            reader = ndjson.reader(f)
            for post in reader:
                yield post


def concat_context(context: List[dict], end_token: str = " [END] ") -> str:
    tweets_list = [tweet["text"] for tweet in context]
    return end_token.join(tweets_list)


def tweet_from_context(context: List[dict]) -> dict:
    return context[-1]


if __name__ == "__main__":
    # test functions
    context_path = "tweet_threads_2019-05-22_2019-06-05.ndjson"
    for i, context in enumerate(ndjson_gen(context_path)):
        if i == 5:
            break
        print("------ \n")
        concat_context_ = concat_context(context)
        print(concat_context_, "\n")
        tweet = tweet_from_context(context)
        print(tweet["text"], "\n\n")
