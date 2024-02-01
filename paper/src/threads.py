"""Extracting longest thread from twitter corpus."""

import os
from glob import glob
import ndjson


def ndjson_gen(filepath: str):
    for file in glob(filepath):
        with open(file) as f:
            reader = ndjson.reader(f)

            for post in reader:
                yield post


### Longest thread ####
def longest_thread(tweets: list):
    conversations: dict = {}
    conversation_start: dict = {}
    in_reply_to: dict = {}
    for tweet in tweets:
        conv_id = tweet["conversation_id"]
        if conv_id not in conversations.keys():
            conversations[conv_id] = {"replies": []}

        if "in_reply_to_user_id" in tweet.keys():
            conversations[conv_id]["replies"].append(tweet["id"])

            if "referenced_tweets" not in tweet.keys():
                print("reply but no reference?")
                continue

            for ref in tweet["referenced_tweets"]:
                if ref["type"] == "replied_to":
                    replied_to_id = ref["id"]
                    if replied_to_id not in in_reply_to.keys():
                        in_reply_to[replied_to_id] = [tweet]
                    else:
                        in_reply_to[replied_to_id].append(tweet)
        else:
            conversations[conv_id]["start"] = tweet["id"]
            conversation_start[conv_id] = tweet

    def find_longest_thread(tweet: dict, in_reply_to: dict):
        if tweet["id"] not in in_reply_to.keys():
            return [tweet]

        thread: list = []
        for reply in in_reply_to[tweet["id"]]:
            tmp_thread = find_longest_thread(reply, in_reply_to)
            if len(tmp_thread) > len(thread):
                thread = tmp_thread

        thread.insert(0, tweet)
        return thread

    no_reply_tweets = 0
    threads: dict = {}
    for conv_id, conv_tweets in conversations.items():
        if "start" not in conv_tweets.keys():
            continue

        threads[conv_id] = find_longest_thread(conversation_start[conv_id], in_reply_to)

        if len(threads[conv_id]) > 1:
            print("\n\n THREAD STARTS: \n")
            print(f"Conversation id: {conv_id}")
            for t in threads[conv_id]:
                print("\n-----------\n")
                print(t["text"])
            print("\n-----------\n")
        else:
            no_reply_tweets += 1

    print(f"{no_reply_tweets} tweets with no reply out of {len(threads)}")


### context window thread ###
def context_window_thread(tweets):
    conversations: dict = {}
    for tweet in tweets:
        conv_id = tweet["conversation_id"]
        if conv_id not in conversations.keys():
            conversations[conv_id] = {tweet["id"]: tweet}

        else:
            conversations[conv_id][tweet["id"]] = tweet

    def find_reply_to_id(tweet: dict):
        if "referenced_tweets" not in tweet.keys():
            Warning("reply but no reference?")
            return None

        for ref in tweet["referenced_tweets"]:
            if ref["type"] == "replied_to":
                return ref["id"]

    def find_context(tweet: dict, conversation: dict, context_length=4):
        if "in_reply_to_user_id" in tweet.keys():
            if context_length == 0:
                return [tweet]
            else:
                if "referenced_tweets" not in tweet.keys():
                    Warning("reply but no reference?")
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

    for tweet in tweets:
        context = find_context(tweet, conversations[tweet["conversation_id"]])

        if len(context) > 1:
            print(f'TWEET ID: {tweet["id"]}')
            for context_tweet in context:
                print(context_tweet["text"])
                print("\n-----------\n")


if __name__ == "__main__":
    path = os.path.join("/data", "004_twitter-stopword", "*.ndjson")

    tweets = []
    for i, post in enumerate(ndjson_gen(path)):
        tweets.append(post)
        if i == 1000:
            break

    context_window_thread(tweets)
