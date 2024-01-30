import json
import multiprocessing.pool

from conspiracies.common.fileutils import iter_lines_of_files
from conspiracies.document import Document
from conspiracies.preprocessing.create_context_threads import context_window_thread
from conspiracies.preprocessing.preprocessor import Preprocessor

# TODO: Due to the way contexts are found and handled which requires all tweets to be
#  loaded in memory, this is not gonna scale very well for large datasets. At the
#  moment, contexts are found by only loading what is needed for the contexts, i.e.
#  less metadata, and then outputting that, and handling metadata on its own. That
#  means two data passes though.
#  It must be possible to avoid having it all in memory, e.g. a join operation in
#  Pandas or Spark. Can we avoid two data-passes in that case?


class TweetsPreprocessor(Preprocessor):
    CONTENT_FIELDS = {
        "id",
        "conversation_id",
        "referenced_tweets",
        "text",
        "in_reply_to_user_id",
    }

    def __init__(
        self,
        n_cores: int = 1,
        context_len: int = 2,
    ):
        super().__init__(n_cores=n_cores)
        self.context_len = context_len

    def do_preprocess_docs(self, glob_pattern: str):
        lines = iter_lines_of_files(glob_pattern)
        tweets = []
        if self.n_cores > 1:
            with multiprocessing.pool.Pool(processes=self.n_cores) as p:
                for result in p.imap_unordered(json.loads, lines, chunksize=100):
                    tweets.append(result)
        else:
            for line in lines:
                tweets.append(json.loads(line))

        tweets_with_context = context_window_thread(tweets, self.context_len)
        for tweet_with_context in tweets_with_context:
            context_tweets, tweet = tweet_with_context[:-1], tweet_with_context[-1]
            doc_id = tweet["id"]
            metadata = {k: v for k, v in tweet.items() if k != "text"}
            text = tweet["text"]
            context = "\n".join(t["text"] for t in context_tweets)
            yield Document(id=doc_id, metadata=metadata, text=text, context=context)
