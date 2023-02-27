from abc import abstractmethod
from typing import List, Tuple, Optional, Dict
from spacy.tokens import Doc
from conspiracies.prompt_relation_extraction.data_classes import SpanTriplet


class Template:
    """Abstract class for template classes. The class is used to create a
    template for the triplet extraction task. The template is used to create a
    prompt for the GPT-3 model.

    Methods:
        generate_prompt(target_tweet, generate_string):
            creates a prompt for the GPT-3 model with the given target tweet. boolean option to generate the string over
        set_examples(examples):
            sets the examples to be used in the prompt
        set_task_description(task_description):
            sets the task description to be used in the prompt
    """

    def __init__(
        self,
        examples: List[Dict[str, str]],
        task_description: str,
    ):
        self.examples = examples
        self.task_description = task_description
        self.spacy_examples_to_list()
        self.generate_prompt(generate_string=True)

    def set_examples(self, examples: List[Tuple[Doc, List[SpanTriplet]]]):
        self.examples = examples
        self.spacy_examples_to_list()
        self.generate_prompt(generate_string=True)

    def set_task_description(self, task_description: str):
        self.task_description = task_description
        self.spacy_examples_to_list()
        self.generate_prompt(generate_string=True)

    @staticmethod
    def get_list_triplets(triplets: List[SpanTriplet]):
        return [
            [triplet.subject.text, triplet.predicate.text, triplet.object.text]
            for triplet in triplets
        ]

    def spacy_examples_to_list(self):
        self.non_spacy = [
            (example["doc"].text, self.get_list_triplets(example["triplets"]))
            for example in self.examples
        ]

    @abstractmethod
    def generate_prompt(self):
        pass

    def __str__(self):
        return self.__name__

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
            for tweet, triplets in self.non_spacy:
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
            tweets, tweet_triplets = zip(*self.non_spacy)

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
            for example, triplets in self.non_spacy:
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
            for example, triplets in self.non_spacy:
                tweet_string += example + "\n\n" + header
                for triplet in triplets:
                    tweet_string += f"\n| {triplet[0]} | {triplet[1]} | {triplet[2]} |"
                tweet_string += "\n\n"
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + target_tweet + "\n\n" + header + "\n"


class PromptTemplate5(Template):
    @staticmethod
    def create_html_example(doc: Doc, triplets: List[SpanTriplet]) -> str:
        """This function creates an html example from a spacy doc and a list of
        triplets. It inserts html tags around the subject, predicate and object
        of each triplet based on the start and end index of the span.

        Args:
            doc (Doc): The spacy doc to insert the html tags into.
            triplets (SpanTriplet): The triplets specifying the subjects, predicates and objects.

        Returns:
            str: The doc with html tags around the subjects, predicates and objects of each triplet
        """
        result_string = ""
        for i, d in enumerate(doc):
            for n, triplet in enumerate(triplets, 1):
                if triplet.subject.end == i:
                    result_string += f"</subject-{n}>"
                if triplet.object.end == i:
                    result_string += f"</object-{n}>"
                if triplet.predicate.end == i:
                    result_string += f"</predicate-{n}>"

                if triplet.subject.start == i:
                    result_string += f"<subject-{n}>"
                if triplet.object.start == i:
                    result_string += f"<object-{n}>"
                if triplet.predicate.start == i:
                    result_string += f"<predicate-{n}>"
            result_string += d.text_with_ws
        return result_string

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
            for example in self.examples:
                tweet_string += (
                    example["doc"].text
                    + "\n"
                    + self.create_html_example(example["doc"], example["triplets"])
                    + "\n\n"
                )
            self.prompt = tweet_string

        if target_tweet:
            return self.prompt + target_tweet + "\n"
