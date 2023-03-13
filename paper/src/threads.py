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


path = os.path.join("/data", "004_twitter-stopword", "*.ndjson")

tweets = []
for i, post in enumerate(ndjson_gen(path)):
    tweets.append(post)
    if i == 1000:
        break

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


def find_thread(tweet: dict, in_reply_to: dict):
    if tweet["id"] not in in_reply_to.keys():
        return [tweet]

    thread: list = []
    for reply in in_reply_to[tweet["id"]]:
        tmp_thread = find_thread(reply, in_reply_to)
        if len(tmp_thread) > len(thread):
            thread = tmp_thread

    thread.insert(0, tweet)
    return thread


no_reply_tweets = 0
threads: dict = {}
for conv_id, conv_tweets in conversations.items():
    if "start" not in conv_tweets.keys():
        continue

    threads[conv_id] = find_thread(conversation_start[conv_id], in_reply_to)

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
