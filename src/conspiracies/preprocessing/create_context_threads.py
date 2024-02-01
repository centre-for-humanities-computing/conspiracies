"""Extracting context threads from twitter corpus."""

import os
from glob import glob
import ndjson
import argparse
import datetime
import re


def ndjson_gen(filepath: str):
    """Creates a generator for ndjson files and yields the tweets without
    retweets."""
    for file in glob(filepath):
        print("Reading file:", file)
        with open(file) as f:
            reader = ndjson.reader(f)
            for post in reader:
                if re.search("^RT", post["text"]):  # remove retweets
                    continue
                yield post


def context_window_thread(tweets, context_len):
    """
    Extracts a thread of context tweets; the last tweet in the thread is the one that the context relates to
    Args:
        tweets: list of tweets
        context_len: number of tweets to include in context
    Returns:
        contexts: list of contexts, where each context is a list of tweets
    """
    conversations = {}
    for tweet in tweets:
        conv_id = tweet["conversation_id"]
        # create a new conversation if it doesn't exist
        conversations.setdefault(conv_id, {})
        conversations[conv_id][tweet["id"]] = tweet

    def find_context(tweet, conversation, context_length=context_len):
        # if the tweet is the first tweet in the conversation or the context length is 0, return the tweet
        if (
            "in_reply_to_user_id" not in tweet
            or context_length == 0
            or "referenced_tweets" not in tweet
        ):
            return [tweet]
        # find the tweet that this tweet is replying to
        replied_to_refs = [
            ref for ref in tweet["referenced_tweets"] if ref["type"] == "replied_to"
        ]
        # if the tweet is not replying to another tweet, return the tweet
        if not replied_to_refs:
            return [tweet]
        # if the tweet is replying to another tweet, find the context for that tweet
        reply_to_id = replied_to_refs[0]["id"]
        # if the tweet is replying to a tweet that is not in the conversation, return the tweet
        if reply_to_id not in conversation:
            return [tweet]
        # find the context for the tweet that this tweet is replying to and add the tweet to the context
        context = find_context(
            conversation[reply_to_id],
            conversation,
            context_length=context_length - 1,
        )
        return context + [tweet]

    # find the context for each tweet in the conversation and return the contexts that are longer than 1 tweet
    contexts = [
        find_context(tweet, conversations[tweet["conversation_id"]]) for tweet in tweets
    ]
    return contexts


def range_of_dates(start_date, extra_days):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    date_range = [start_date + datetime.timedelta(days=x) for x in range(extra_days)]
    return date_range


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get tweets + context from date range")
    parser.add_argument(
        "-s",
        "--start_date",
        type=str,
        default="2019-05-22",
        help="start date in format YYYY-MM-DD",
    )
    parser.add_argument(
        "-e",
        "--extra_days",
        type=int,
        default=15,
        help="number of days to include from start date and after",
    )
    parser.add_argument(
        "-p",
        "--data_path",
        type=str,
        default="da_stopwords_part?_2019-01-01_2020-12-31.ndjson",
        help='path to ndjson file; for all: "*.ndjson"',
    )
    parser.add_argument(
        "-c",
        "--context_len",
        type=int,
        default=4,
        help="number of tweets to include in context",
    )
    args = parser.parse_args()

    # path to twitter data
    path = os.path.join("/data", "004_twitter-stopword", args.data_path)

    date_range = range_of_dates(args.start_date, args.extra_days)
    print(date_range)
    print(
        f"Looking for tweets from {args.start_date} and {args.extra_days} days forward (to and indcluding: {datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() + datetime.timedelta(days=args.extra_days-1)})",
    )
    tweets = []

    for i, post in enumerate(ndjson_gen(path)):
        # get the date of the tweet and append the tweet if it is within the date range
        date_ = datetime.datetime.strptime(post["created_at"][0:10], "%Y-%m-%d").date()
        if date_ in date_range:
            tweets.append(post)
        # if len(tweets) > 1000:
        #     break
    print(f"Found {len(tweets)} tweets in the date range (out of {i} tweets total)")

    # run the tweet thread extraction
    contexts = context_window_thread(tweets, args.context_len)

    # write contests to ndjson; the ndjson of contexts has the format: List[Dict[str, Any]]
    with open(
        os.path.join(
            f"tweet_threads_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() }_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() + datetime.timedelta(days=args.extra_days-1)}.ndjson",
        ),
        "w",
    ) as f:
        ndjson.dump(contexts, f)
