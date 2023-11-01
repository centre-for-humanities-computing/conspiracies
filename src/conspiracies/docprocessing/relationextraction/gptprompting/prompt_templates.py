"""PromptTemplate abstract class along with the instances of the class."""

import re
from abc import abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union

from confection import registry
from spacy.tokens import Doc

from conspiracies.docprocessing.relationextraction.data_classes import (
    SpanTriplet,
    StringTriplet,
)


class PromptTemplate:
    """Abstract class for template classes.

    The class is used to create a template for the triplet extraction
    task. The template is used to create a prompt for generative models
    such as GPT-3 and chatGPT.
    """

    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        """
        Args:
            examples: A tuple of a spacy Docs
            task_description: A description of the task
        """

        self.examples = examples
        if task_description:
            self.task_description = task_description
        else:
            self.task_description = "Extract triplets on the form \
(Subject - predicate - object) from the following tweet. \
First, you will see a few examples."

    @abstractmethod
    def create_prompt(self, target: str) -> Union[str, List[Dict[str, str]]]:
        """Create a prompt based on the task description and examples and
        target."""
        pass

    @abstractmethod
    def parse_prompt(self, prompt: str, target_tweet: str) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets."""
        pass

    def set_examples(self, examples: List[Doc]):
        """Updates examples."""
        self.examples = examples


@registry.prompt_templates("conspiracies/template_1")
class PromptTemplate1(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        super().__init__(task_description=task_description, examples=examples)
        if not task_description:
            self.task_description = """Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less. 
They should be presented with each element in parentheses as shown below:"""  # noqa: E501

    def create_prompt(
        self,
        target: str = "",
    ) -> str:
        """Create a prompt template on the form

        ```
        {task_description}

        Tweet: {tweet1}
        Triplet: {triplets1}
        ...
        Tweet: {tweetN}
        Triplet: {tripletsN}

        Tweet: {target_tweet}
        ```

        Args:
            target: The tweet to be annotated.
        """
        examples_str = "---\n\n"
        for tweet in self.examples:
            triplets = tweet._.relation_triplets
            examples_str += f"Tweet: {tweet.text}\n"

            if len(triplets) == 0:
                examples_str += "Triplets: Null \n\n"
            else:
                for i, triplet in enumerate(triplets):
                    triplet_str = "({subj}) ({pred}) ({obj})"
                    triplet_str = triplet_str.format(
                        subj=triplet.subject.text,
                        pred=triplet.predicate.text,
                        obj=triplet.object.text,
                    )
                    if i == 0:
                        examples_str += f"Triplets: {triplet_str}\n"
                    else:
                        examples_str += f"\t{triplet_str}\n"

            examples_str += "---\n"
            tweet_string = f"{self.task_description}\n\n{examples_str}\nTweet: "
            prompt = tweet_string

        return prompt + f"{target}\nTriplets:"

    @staticmethod
    def create_string_triplets(tweet, triplet):
        subject, predicate, object = triplet
        return StringTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
            text=tweet,
        )

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets."""

        def strip_triplet(triplet):
            return [
                elem
                for elem in [element.replace(")", "").strip() for element in triplet]
                if elem not in ["", " "]
            ]

        data = [row for row in prompt_response.split("\n") if row not in ["", "---"]]
        triplets = []
        for line in data:
            tmp_triplet = line.split("(")
            triplet = strip_triplet(tmp_triplet)
            if len(triplet) == 3:
                triplets.append(self.create_string_triplets(target_tweet, triplet))
        return triplets


@registry.prompt_templates("conspiracies/template_2")
class PromptTemplate2(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        super().__init__(task_description=task_description, examples=examples)
        if not task_description:
            self.task_description = """Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less. 
They should be presented with each element in parentheses as shown below:"""  # noqa: E501

    def create_prompt(
        self,
        target: str = "",
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
        tweets_block = "---\n\n"
        tweets = self.examples
        tweet_triplets = [tweet._.relation_triplets for tweet in tweets]
        for tweet in tweets:
            tweets_block += f"Tweet: {tweet.text}\n\n"

        triplet_block = ""
        for triplets in tweet_triplets:
            if len(triplets) == 0:
                triplet_block += "Triplets:\n"
                continue
            for i, triplet in enumerate(triplets):  # type: ignore
                triplet_str = "({subj}) ({pred}) ({obj})"
                triplet_str = triplet_str.format(
                    subj=triplet.subject.text,
                    pred=triplet.predicate.text,
                    obj=triplet.object.text,
                )
                if i == 0:
                    triplet_block += f"Triplets: {triplet_str}\n"
                else:
                    triplet_block += f"\t{triplet_str}\n"
        triplet_block += "\n---\n\n"
        prompt = f"{self.task_description}\n\n{tweets_block}\n{triplet_block}"

        return prompt + f"Tweet: {target}\n\nTriplets:"

    @staticmethod
    def create_string_triplets(tweet, triplet):
        subject, predicate, object = triplet
        return StringTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
            text=tweet,
        )

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets."""

        def strip_triplet(triplet):
            return [
                elem
                for elem in [element.replace(")", "").strip() for element in triplet]
                if elem not in ["", " "]
            ]

        data = [row for row in prompt_response.split("\n") if row not in ["", "---"]]
        triplets = []
        for line in data:
            tmp_triplet = line.split("(")
            triplet = strip_triplet(tmp_triplet)
            if len(triplet) == 3:
                triplets.append(self.create_string_triplets(target_tweet, triplet))
        return triplets


@registry.prompt_templates("conspiracies/markdown_template_1")
class MarkdownPromptTemplate1(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        super().__init__(task_description=task_description, examples=examples)
        if not task_description:
            self.task_description = """Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less. 
They should be put in a markdown table as shown below:"""  # noqa: E501

    def create_prompt(
        self,
        target: str = "",
    ) -> str:
        """Create a prompt template on the form

        ```
        {task_description}

        | Tweet | Subject | Predicate | Object |
        | --- | --- | --- | --- |
        | {tweet 1} | {subject 1} | {predicate 1} | {object 1} |
        |           | {subject 2} | {predicate 2} | {object 2} |
        ...
        | {tweet n} | {subject 1} | {predicate 1} | {object 1} |
        |           | {subject 2} | {predicate 2} | {object 2} |
        | {target_tweet} |
        ```
        """
        tweet_string = f"{self.task_description}\n| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |"  # noqa: E501
        for example in self.examples:
            triplets = example._.relation_triplets
            if len(triplets) == 0:
                tweet_string += f"\n| {example} | | | |"
                continue
            for i, triplet in enumerate(triplets):
                subj = triplet.subject.text
                pred = triplet.predicate.text
                obj = triplet.object.text

                if i == 0:
                    tweet_string += f"\n| {example} | {subj} | {pred} | {obj} |"
                else:
                    tweet_string += f"\n| | {subj} | {pred} | {obj} |"
        prompt = tweet_string

        return prompt + f"\n| {target} |"

    @staticmethod
    def create_string_triplets(tweet, triplet):
        subject, predicate, object = triplet
        return StringTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
            text=tweet,
        )

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets."""
        text = prompt_response.replace(self.task_description, "")
        data = [row for row in text.split("\n") if row != ""]
        triplets: List[StringTriplet] = []

        for row in data:
            elements = [
                element.strip()
                for element in row.split("|")
                if element not in ["", " "]
            ]
            # If the response has added another tweet, return triplets as is now
            if len(elements) == 4:
                return triplets
            # If there are only three elements they are triplets for the current tweet
            elif len(elements) == 3:
                as_string_triplet = self.create_string_triplets(target_tweet, elements)
                triplets.append(as_string_triplet)

        return triplets


@registry.prompt_templates("conspiracies/markdown_template_2")
class MarkdownPromptTemplate2(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        super().__init__(task_description=task_description, examples=examples)
        if not task_description:
            self.task_description = """Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less. 
They should be put in a markdown table as shown below:"""  # noqa: E501

    def create_prompt(
        self,
        target: str = "",
    ) -> str:
        """Create a prompt template on the form.

        ```
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
        ```
        """
        header = "| Subject | Predicate | Object |\n| --- | --- | --- |"

        tweet_string = f"{self.task_description}\n\n"
        for example in self.examples:
            triplets = example._.relation_triplets
            tweet_string += example.text + "\n\n" + header
            if len(triplets) == 0:
                tweet_string += "\n\n"
                continue
            for triplet in triplets:
                subj = triplet.subject.text
                pred = triplet.predicate.text
                obj = triplet.object.text

                tweet_string += f"\n| {subj} | {pred} | {obj} |"
            tweet_string += "\n\n"
        prompt = tweet_string

        return prompt + target + "\n\n" + header + "\n"

    @staticmethod
    def create_string_triplets(tweet, triplet):
        subject, predicate, object = triplet
        return StringTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
            text=tweet,
        )

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets.

        Ignores extracted triplets that do not contain exactly three
        elements
        """
        # Remove task description
        text = prompt_response.replace(self.task_description, "")
        data = [row for row in text.split("\n") if row != ""]
        triplets: List[StringTriplet] = []

        for row in data:
            elements = [element.strip() for element in row.split("|") if element != ""]
            # If the response has added another tweet, return triplets as is now
            if len(elements) == 4:
                return triplets
            # If there are only three elements they are triplets for the current tweet
            elif len(elements) == 3:
                as_string_triplet = self.create_string_triplets(target_tweet, elements)
                triplets.append(as_string_triplet)

        return triplets


@registry.prompt_templates("conspiracies/xml_style_template")
class XMLStylePromptTemplate(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
        tags: List[str] = ["subject", "predicate", "object"],
    ):
        super().__init__(task_description=task_description, examples=examples)
        self.tags = tags
        if not task_description:
            self.task_description = """Tag the following tweet with triplets using HTML tags.
Semantic triplets consists of the elements subject, verb phrase and object. The verb phrase includes all particles and modifyers.
There should always be exactly three elements in a triplet, no more no less.
The subject is enclosed between <subject-n> and </subject-n>, the verb phrase between <predicate-n> and </predicate-n> and the object between <object-n> and </object-n>.
n is the number of the triplet, starting at 1. Elements of one triplet can be contained within elements of another triplet.
The triplets should be tagged in the tweet as shown below:"""  # noqa: E501

    @staticmethod
    def create_xml_example(doc: Doc, triplets: List[SpanTriplet]) -> str:
        """This function creates an XML-like prompt from a spacy doc and a list
        of triplets. It inserts XML tags around the subject, predicate and
        object of each triplet based on the start and end index of the span.

        Args:
            doc: The spacy doc to insert the html tags into.
            triplets: The triplets specifying the subjects, predicates and
                objects.

        Returns:
            The doc with html tags around the subjects, predicates and objects of
                each triplet
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

    def create_prompt(
        self,
        target: str = "",
    ) -> str:
        """Create a prompt template on the form.

        ```
        {task_description}

        {tweet 1}
        {xml_tagged tweet 1}

        ...

        {tweet n}
        {xml_tagged tweet n}

        {target tweet}
        """
        prompt = f"{self.task_description}\n\n"
        for doc in self.examples:
            triplets = doc._.relation_triplets
            prompt += doc.text + "\n" + self.create_xml_example(doc, triplets) + "\n\n"

        return prompt + target + "\n"

    @staticmethod
    def __parse(text: str, tags=["subject", "predicate", "object"]) -> Dict[str, Any]:
        extract_tags = XMLStylePromptTemplate.extract_tags
        remove_tags = XMLStylePromptTemplate.remove_tags
        update_span = XMLStylePromptTemplate.update_span

        tags_info = extract_tags(text, tags)

        open_tags = {}
        closed_tags = {}
        for tag_info in tags_info:
            n = tag_info["n"]
            tag = tag_info["tag"]
            if tag_info["is_close"]:
                closed_tags[f"{tag}-{n}"] = {"span": tag_info["span"]}
            else:
                open_tags[f"{tag}-{n}"] = {"span": tag_info["span"], "tag": tag, "n": n}

        # extract triplets
        triplets = defaultdict(  # type: ignore
            lambda: {"subject": None, "predicate": None, "object": None},
        )
        spans_to_update = []
        for tag_n in open_tags:
            if tag_n in closed_tags:
                content_span = list(
                    (open_tags[tag_n]["span"][1], closed_tags[tag_n]["span"][0]),
                )
                content = text[content_span[0] : content_span[1]]
                tag = open_tags[tag_n]["tag"]
                n = open_tags[tag_n]["n"]
                triplets[n][tag] = {  # type: ignore
                    "text": remove_tags(content),
                    "span": content_span,
                }
                spans_to_update.append(content_span)

        spans_to_remove = [tag_info["span"] for tag_info in tags_info]
        for span in spans_to_update:
            static_span = tuple(span)
            content = text[span[0] : span[1]]

            for span_to_remove in spans_to_remove:
                _span = update_span(static_span, span_to_remove)  # type: ignore
                span[0] += _span[0]
                span[1] += _span[1]

        return {"text": remove_tags(text), "triplets": triplets}

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets.

        Does not use the target_tweet, but required for consistency
        """
        parse = self.__parse(prompt_response, tags=self.tags)

        def to_string_triplet(triplet):
            return StringTriplet(
                subject=triplet["subject"]["text"],
                predicate=triplet["predicate"]["text"],
                object=triplet["object"]["text"],
                subject_char_span=triplet["subject"]["span"],
                predicate_char_span=triplet["predicate"]["span"],
                object_char_span=triplet["object"]["span"],
                text=parse["text"],
            )

        triplets = []

        for n, triplet in parse["triplets"].items():
            # NB Shouldnt this be taken care of earlier??
            if (
                triplet["subject"] is not None
                and triplet["predicate"] is not None
                and triplet["object"] is not None
            ):
                str_triplet = to_string_triplet(triplet)
                triplets.append(str_triplet)
        return triplets

    @staticmethod
    def extract_tags(
        text: str,
        tags: List[str] = ["subject", "predicate", "object"],
    ) -> List[dict]:
        """Extractss all tags on the form: <{tag}-{n}>{content}</{tag}-{n}>

        and returns a dict on the form:
        {tag: tag, span: (start, end), n: n, is_close: bool}
        """
        # create regex pattern to match both start and close tags
        pattern = r"<[/]?(" + "|".join(tags) + r")-\d+>"

        def extract_tag_info(match):
            tag = match.group()[1:-1]
            is_close = tag.startswith("/")
            if is_close:
                tag = tag[1:]
            tag, n = tag.split("-")
            return {"tag": tag, "span": match.span(), "n": n, "is_close": is_close}

        return [extract_tag_info(m) for m in re.finditer(pattern, text)]

    @staticmethod
    def remove_tags(text: str) -> str:
        """Remove all tags from a string."""
        return re.sub(r"<[/]?\w+-\d+>", "", text)

    @staticmethod
    def update_span(
        span: Tuple[int, int],
        deleted_span: Tuple[int, int],
    ) -> Tuple[int, int]:
        """Updates a span by after a part of the text has been deleted."""
        diff = deleted_span[1] - deleted_span[0]

        # if deleted span is before span
        if span[0] >= deleted_span[1]:
            return -diff, -diff
        # if deleted span is after span
        if span[1] <= deleted_span[0]:
            return 0, 0
        # if deleted span is inside span
        if span[0] <= deleted_span[0] and span[1] >= deleted_span[1]:
            return 0, -diff
        # if deleted span is overlapping start of span
        if span[0] < deleted_span[0] and span[1] < deleted_span[1]:
            return 0, deleted_span[0] - span[1]
        # if deleted span is overlapping end of span
        if span[0] > deleted_span[0] and span[1] > deleted_span[1]:
            return deleted_span[1] - span[0], 0
        # if deleted span is equal to span
        if span[0] == deleted_span[0] and span[1] == deleted_span[1]:
            raise ValueError("Span to delete is equal to span to update")
        raise ValueError("Unknown error")


@registry.prompt_templates("conspiracies/chatgpt_style_template")
class chatGPTPromptTemplate(PromptTemplate):
    def __init__(
        self,
        examples: List[Doc],
        task_description: Optional[str] = None,
    ):
        super().__init__(task_description=task_description, examples=examples)
        if not task_description:
            self.task_description = """I need you to extract semantic triplets from tweets. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less, and they should be presented in a markdown table.
First, I will provide you with a few examples."""  # noqa: E501

    def create_prompt(self, target: str) -> List[Dict[str, str]]:
        """Create a prompt for the chatGPT model. Form is:
        [
        {"role": "system",
         "content": "You are a helpful assistant who is also an expert linguist. "
        },
        {"role": "user",
         "content": "Hi, I need your help on a linguistic question."
        },
        {"role": "assistant",
         "content": "Sure, what is the task?"
        },
        {"role": "user",
         "content": task_description
        },
        {"role": "assistant",
         "content": "That sounds like something I can help you with. Let me see the examples."
        },
        {"role": "user",
            "content": "The tweet is:\n{example_1}\nThe triplets in the tweet are:{triplet_1\ntriplets_2}\n"
        },
        {"role": "assistant",
        "content": "Yes I see! What is the next tweet and triplets?\n"
        },

        ...

        {"role": "user",
         "content": "The tweet is:\n{example_n}\nThe triplets in the tweet are:{triplet_1\n ... triplet_m}\n"
        },
        {"role": "user",
         "content": 'All right, now you try. The tweet is:\n{target}\nWhat are the triplets?'
        },
        ]
        """  # noqa: E501
        message_dicts = [
            {
                "role": "system",
                "content": "You are a helpful assistant \
who is also an expert linguist. ",
            },
            {
                "role": "user",
                "content": "Hi, I need your help on a linguistic question.",
            },
            {
                "role": "assistant",
                "content": "Sure, what is the task?",
            },
            {
                "role": "user",
                "content": self.task_description,
            },
            {
                "role": "assistant",
                "content": "That sounds like something I can help you with. \
Let me try the first example!",
            },
        ]
        for i, example in enumerate(self.examples):
            triplets = example._.relation_triplets
            if i == 0:
                message_dicts.append(
                    {
                        "role": "user",
                        "content": f"The tweet is:\n{example.text}\n",
                    },
                )
            else:
                message_dicts.append(
                    {
                        "role": "user",
                        "content": f"Correct! The next tweet is:\n{example.text}\n",
                    },
                )
            message_string = "I extracted the following triplets:\n"
            for triplet in triplets:
                message_string += (
                    f"\t{triplet.subject} - {triplet.predicate} - {triplet.object}\n"
                )
            message_dicts.append(
                {
                    "role": "assistant",
                    "content": message_string,
                },
            )
        message_dicts.append(
            {
                "role": "user",
                "content": f"The tweet is:\n{target}\n",
            },
        )
        return message_dicts

    @staticmethod
    def create_string_triplets(tweet, triplet):
        subject, predicate, object = triplet
        return StringTriplet(
            subject=subject,
            predicate=predicate,
            object=object,
            text=tweet,
        )

    def parse_prompt(
        self,
        prompt_response: str,
        target_tweet: str,
    ) -> List[StringTriplet]:
        """Parse a prompt into a target tweet and triplets.

        Ignores extracted triplets that do not contain exactly three
        elements
        """

        triplets: List[StringTriplet] = []
        lines = [
            line.strip()
            for line in prompt_response.split("\n")
            if line not in ["", " "]
        ]
        for line in lines:
            if "-" in line:
                extractions = [element.strip() for element in line.split("-")]
                if len(extractions) == 3:
                    triplets.append(
                        self.create_string_triplets(target_tweet, extractions),
                    )
        return triplets
