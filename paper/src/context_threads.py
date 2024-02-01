"""Extracting longest thread from twitter corpus."""

import os
from glob import glob
import ndjson
import argparse
import datetime
import re


def ndjson_gen(filepath: str):
    """Creates a generator for ndjson files and yields the tweets."""
    for file in glob(filepath):
        print("Reading file:", file)
        with open(file) as f:
            reader = ndjson.reader(f)
            for post in reader:
                if re.search("^RT", post["text"]):  # remove retweets
                    continue
                yield post


'''
### context window thread ###
def context_window_thread(tweets, context_len, start_date, extra_days):
    """
    Extracts a thread of context tweets; the last tweet in the thread is the one that the context relates to
    Args:
        tweets: list of tweets
        context_len: number of tweets to include in context
        start_date: start date of the date range
        extra_days: number of days to include from start date and after
    Returns:
        contexts: list of contexts, where each context is a list of tweets
    """
    conversations: dict = {}
    # loop over tweets and create conversation dicts
    for tweet in tweets:
        
        conv_id = tweet["conversation_id"]
        if conv_id not in conversations.keys():
            conversations[conv_id] = {tweet["id"]: tweet}

        else:
            conversations[conv_id][tweet["id"]] = tweet

    def find_reply_to_id(tweet: dict):
        """
        Find the id of the tweet this tweet is replying to
        """
        for ref in tweet["referenced_tweets"]:
            if ref["type"] == "replied_to":
                return ref["id"]

    def find_context(tweet: dict, conversation: dict, context_length: int = context_len):
        if "in_reply_to_user_id" in tweet.keys():
            if context_length == 0:
                return [tweet]
            else:
                if "referenced_tweets" not in tweet.keys():
                    #raise Warning("reply but no reference?") #googl
                    print("reply but no reference?") 
                    return [tweet]

                reply_to_id = find_reply_to_id(tweet)
                try:
                    reply_to = conversation[reply_to_id]
                except KeyError:
                    
                    return [tweet]

                context = find_context(
                    reply_to,
                    conversation,
                    context_length=context_length - 1,
                )
                context.append(tweet)
                return context
        else:
            return [tweet]
    
    contexts = []
    for tweet in tweets:
        context = find_context(tweet, conversations[tweet["conversation_id"]], context_length=context_len)
        
        if len(context) > 1:
            contexts.append(context)
        elif len(context) >= context_len+1:
            print("context length too long:", len(context))
            break
    return contexts
'''


def context_window_thread(tweets, context_len):
    """
    Extracts a thread of context tweets; the last tweet in the thread is the one that the context relates to
    Args:
        tweets: list of tweets
        context_len: number of tweets to include in context
        start_date: start date of the date range
        extra_days: number of days to include from start date and after
    Returns:
        contexts: list of contexts, where each context is a list of tweets
    """
    conversations = {}
    for tweet in tweets:
        conv_id = tweet["conversation_id"]
        conversations.setdefault(conv_id, {})
        conversations[conv_id][tweet["id"]] = tweet

    def find_context(tweet, conversation, context_length=context_len):
        if "in_reply_to_user_id" not in tweet:
            return [tweet]

        if context_length == 0 or "referenced_tweets" not in tweet:
            return [tweet]

        replied_to_refs = [
            ref for ref in tweet["referenced_tweets"] if ref["type"] == "replied_to"
        ]
        if replied_to_refs:
            reply_to_id = next(ref["id"] for ref in replied_to_refs)
            try:
                reply_to = conversation[reply_to_id]
            except KeyError:
                return [tweet]

            context = find_context(
                reply_to,
                conversation,
                context_length=context_length - 1,
            )
            context.append(tweet)
            return context
        else:
            # handle the case where no replied_to reference is found
            return [tweet]

    contexts = [
        find_context(tweet, conversations[tweet["conversation_id"]])
        for tweet in tweets
        if len(find_context(tweet, conversations[tweet["conversation_id"]])) > 1
    ]
    return contexts


def range_of_dates(start_date, extra_days):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    date_range = [start_date + datetime.timedelta(days=x) for x in range(extra_days)]
    return date_range


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get tweets + context from date range")
    parser.add_argument(
        "--start_date",
        type=str,
        default="2019-05-22",
        help="start date in format YYYY-MM-DD",
    )
    parser.add_argument(
        "--extra_days",
        type=int,
        default=15,
        help="number of days to include from start date and after",
    )
    parser.add_argument(
        "--data_path",
        type=str,
        default="da_stopwords_part?_2019-01-01_2020-12-31.ndjson",
        help='path to ndjson file; for all: "*.ndjson"',
    )
    parser.add_argument(
        "--context_len",
        type=int,
        default=4,
        help="number of tweets to include in context",
    )
    args = parser.parse_args()

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

    print(f"Found {len(tweets)} tweets in the date range (out of {i} tweets total)")
    """#run the tweet thread extraction contexts =
    context_window_thread(tweets, args.context_len, args.start_date,
    args.extra_days)

    #write contests to ndjson
    with open(os.path.join(f"tweetcontexts_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() }_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() + datetime.timedelta(days=args.extra_days-1)}.ndjson"), "w") as f:
        ndjson.dump(contexts, f) #the ndjson of contexts has the format: List[Dict[str, Any]]
    """
    # CHATGPT
    # run the tweet thread extraction
    contexts = context_window_thread(tweets, args.context_len)

    # write contests to ndjson
    with open(
        os.path.join(
            f"tweet_threads_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() }_{datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date() + datetime.timedelta(days=args.extra_days-1)}.ndjson",
        ),
        "w",
    ) as f:
        ndjson.dump(
            contexts,
            f,
        )  # the ndjson of contexts has the format: List[Dict[str, Any]]
