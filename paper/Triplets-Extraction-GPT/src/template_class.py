from abc import abstractmethod
from typing import List, Tuple, Optional


class Template:
    def __init__(
        self,
        examples: List[Tuple],
        task_description: str,
    ):
        self.examples = examples
        self.task_description = task_description
        self.generate_prompt(generate_string=True)

    def set_examples(self, examples: List[Tuple]):
        self.examples = examples
        self.generate_prompt(generate_string=True)

    def set_task_description(self, task_description: str):
        self.task_description = task_description
        self.generate_prompt(generate_string=True)

    @abstractmethod
    def generate_prompt(self):
        pass

    def __str__(self):
        return self.__name__


class PromptTemplate1(Template):
    def generate_prompt(
        self,
        target_tweet: Optional[str] = None,
        generate_string: bool = False,
    ) -> str:
        """Create a prompt template on the form '''.

        {task_description}
        Tweet: {tweet1}
        Triplet: {triplets1}
        ...
        Tweet: {tweetN}
        Triplet: {tripletsN}

        Tweet: {target_tweet}
        '''
        """
        if generate_string:
            examples_str = "---\n\n"
            for tweet, triplets in self.examples:
                examples_str += f"Tweet: {tweet}\n"

                if len(triplets) == 0:
                    examples_str += f"Triplet: Null \n\n"
                else:
                    for i, triplet in enumerate(triplets):
                        assert len(triplet) == 3, "len of triplets should be 3"
                        triplet_str = f"({triplet[0]}) ({triplet[1]}) ({triplet[2]})"
                        if i == 0:
                            examples_str += f"Triplets: {triplet_str}\n"
                        else:
                            examples_str += f"\t{triplet_str}\n"

            examples_str += "---\n"
            tweet_string = f"{self.task_description}\n\n{examples_str}\nTweet:"
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + f"{target_tweet}\nTriplets:"


class PromptTemplate2(Template):
    def generate_prompt(
        self,
        target_tweet: Optional[str] = None,
        generate_string: bool = False,
    ) -> str:
        """Create a prompt template on the form '''.

        {task_description}
        Tweet: {tweet1}
        Tweet: {tweet2}
        ...
        Tweet: {tweetN}

        Triplet: {triplets1}
        Triplet: {triplets2}
        ...
        Triplet: {tripletsN}

        Tweet: {target_tweet}
        '''
        """
        if generate_string:
            tweets_block = "---\n\n"
            tweets, tweet_triplets = zip(*self.examples)

            for tweet in tweets:
                tweets_block += f"Tweet: {tweet}\n\n"

            tweet_triplet_str = ""
            for triplets in tweet_triplets:
                for i, triplet in enumerate(triplets):
                    assert len(triplet) == 3, "len of triplets should be 3"
                    triplet_str = f"({triplet[0]}) ({triplet[1]}) ({triplet[2]})"
                    if i == 0:
                        tweet_triplet_str += f"Triplet: {triplet_str}\n"
                    else:
                        tweet_triplet_str += f"\t{triplet_str}\n"
            tweet_triplet_str += "\n---\n\n"
            tweet_string = (
                f"{self.task_description}\n\n{tweets_block}\n{tweet_triplet_str}"
            )
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + f"Tweet: {target_tweet}\n\nTriplets:"


class PromptTemplate3(Template):
    def generate_prompt(
        self,
        target_tweet: Optional[str] = None,
        generate_string: bool = False,
    ) -> str:
        """Create a prompt template on the form

        '''
        {task_description}

        | Tweet | Subject | Predicate | Object |
        | --- | --- | --- | --- |
        | {tweet 1} | {subject 1} | {predicate 1} | {object 1} |
        |           | {subject 2} | {predicate 2} | {object 2} |
        ...
        | {tweet n} | {subject 1} | {predicate 1} | {object 1} |
        |           | {subject 2} | {predicate 2} | {object 2} |
        | {target_tweet} |

        '''
        """
        if generate_string:
            tweet_string = f"{self.task_description}\n| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |"
            for example, triplets in self.examples:
                for i, triplet in enumerate(triplets):
                    assert len(triplet) == 3, "len of triplets should be 3"
                    if i == 0:
                        tweet_string += f"\n| {example} | {triplet[0]} | {triplet[1]} | {triplet[2]} |"
                    else:
                        tweet_string += (
                            f"\n| | {triplet[0]} | {triplet[1]} | {triplet[2]} |"
                        )
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + f"\n| {target_tweet} |"


class PromptTemplate4(Template):
    def generate_prompt(
        self,
        target_tweet: Optional[str] = None,
        generate_string: bool = False,
    ) -> str:
        """Create a prompt template on the form '''.

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
        '''
        """
        header = "| Subject | Predicate | Object |\n| --- | --- | --- |"
        if generate_string:
            tweet_string = f"{self.task_description}\n\n"
            for example, triplets in self.examples:
                tweet_string += example + "\n\n" + header
                for triplet in triplets:
                    tweet_string += f"\n| {triplet[0]} | {triplet[1]} | {triplet[2]} |"
                tweet_string += "\n\n"
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + target_tweet + "\n\n" + header + "\n"


class PromptTemplate5(Template):
    def generate_prompt(
        self,
        target_tweet: Optional[str] = None,
        generate_string: bool = False,
    ) -> str:
        """Create a prompt template on the form.

        {task_description}

        {tweet 1}
        {html_tagged tweet 1}

        ...

        {tweet n}
        {html_tagged tweet n}

        {target tweet}
        """
        if generate_string:
            tweet_string = f"{self.task_description}\n\n"
            for example, html in self.examples:
                assert html is not None, "Example does not seem to contain html-tagging"
                tweet_string += example + "\n" + html + "\n\n"
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + target_tweet + "\n"


if __name__ == "__main__":
    # Example of how to use the templates
    examples = [
        ("This is a tweet", [("this", "is", "a tweet")]),
        ("This is another tweet", [("this", "is", "another tweet")]),
        (
            "This is a third tweet, one that is long and has several triplets",
            [
                ("this", "is", "a third tweet"),
                ("one", "is", "long"),
                ("one", "has", "several triplets"),
            ],
        ),
    ]
    new_examples = [
        ("This is a new example tweet", [("this", "is", "a new example tweet")]),
        (
            "I see you now provide a new example",
            [("I", "see", "you now"), ("you", "provide", "a new example")],
        ),
    ]
    target_tweets = ["Target tweet 1", "Target tweet 2"]
    template = PromptTemplate5(examples, "This is a task description")
    template.set_examples(new_examples)

    for target in target_tweets:
        prompt = template.generate_prompt(target)
        print(prompt + "\n\n")
