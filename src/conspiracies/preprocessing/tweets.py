import json
import logging
from typing import Iterable

from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.document import Document
from conspiracies.preprocessing.create_context_threads import context_window_thread
from conspiracies.preprocessing.preprocessor import Preprocessor

# TODO: Due to the way contexts are found and handled which requires all tweets to be
#  loaded in memory, this is not gonna scale very well for large datasets.


class TweetsPreprocessor(Preprocessor):

    def __init__(
        self,
        metadata_fields: Iterable[str] = ("*",),
        context_length: int = 2,
    ):
        super().__init__(metadata_fields=metadata_fields)
        self.context_length = context_length

    def _do_preprocess_docs(self, glob_pattern: str):
        lines = iter_lines_of_files(glob_pattern)
        tweets = [json.loads(line) for line in lines]

        doc_ids = set()
        tweets_with_context = context_window_thread(tweets, self.context_length)
        for tweet_with_context in tweets_with_context:
            context_tweets, tweet = tweet_with_context[:-1], tweet_with_context[-1]
            doc_id = tweet["id"]
            if doc_id in doc_ids:
                logging.debug("Skipping duplicate %s", doc_id)
                continue
            doc_ids.add(doc_id)
            if (
                "referenced_tweets" in tweet
                and tweet["referenced_tweets"][0]["type"] == "retweeted"
            ):
                logging.debug("Skipping retweet %s", doc_id)
                continue
            metadata = {k: v for k, v in tweet.items() if k != "text"}
            text = tweet["text"]
            context = "\n".join(t["text"] for t in context_tweets)
            yield Document(id=doc_id, metadata=metadata, text=text, context=context)
