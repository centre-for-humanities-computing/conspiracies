import time
import os
import random
from pathlib import Path
from typing import List, Optional, Generator, Union
import spacy
from spacy.tokens import Doc
import argparse

from data import load_gold_triplets
import spacy
from extract_examples import extract_examples
from conspiracies.prompt_relation_extraction import (
    MarkdownPromptTemplate2,
    PromptTemplate,
)
import openai

# Conspiracies
from conspiracies.coref import CoreferenceComponent

from extract_utils import write_txt, ndjson_gen
from src.concat_split_contexts import (
    concat_context,
    tweet_from_context_text,
)


def build_coref_pipeline():
    nlp_coref = spacy.blank("da")
    nlp_coref.add_pipe("sentencizer")
    nlp_coref.add_pipe("allennlp_coref")

    return nlp_coref


def build_headword_extraction_pipeline():
    nlp = spacy.load("da_core_news_sm")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe(
        "heads_extraction",
        config={"normalize_to_entity": True, "normalize_to_noun_chunk": True},
    )
    return nlp


def batch_generator(generator: Generator, n: int):
    """Batches a generator into batches of size n.

    Args:
        generator (Generator): Generator to batch
        n (int): Size of batches

    Yields:
        batch (list): List of elements from generator
    """
    batch = []
    for element in generator:
        batch.append(element)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch


def prepare_template(template: PromptTemplate, n_examples=9, cv=1):
    """Prepares a template by extracting examples from gold docs Uses the
    targets as examples since they are criteria balanced.

    Args:
        template (PromptTemplate): Template to prepare
        n_examples (int, optional): Number of examples to use for prompting.
            Defaults to 10.
        cv (int, optional): Number of times to do the extraction.
            Defaults to 1, since this is only relevant for prompt comparing

    Returns:
        PromptTemplate: the template with examples
    """
    gold_docs = load_gold_triplets(nlp=spacy.load("da_core_news_sm"))
    targets, _ = extract_examples(gold_docs, n_examples, cv)
    return template(examples=targets[0])


def concat_resolve_unconcat_contexts(file_path: str):
    """Concatenates and resolves coreferences in contexts. The resolved
    contexts are then split, and the last (target) tweet is returned.

    Args:
        file_path (str): path to where the contexts are stored

    Returns:
        Generator: a generator with the resolved target tweets
    """
    context_tweets: List[str] = []
    for context in ndjson_gen(file_path):
        concatenated = concat_context(context)
        context_tweets.append(concatenated)

    coref_nlp = build_coref_pipeline()
    coref_docs = coref_nlp.pipe(context_tweets)
    resolved_docs = (d._.resolve_coref for d in coref_docs)

    resolved_tweets = (tweet_from_context_text(tweet) for tweet in resolved_docs)
    return resolved_tweets


def concatenate_tweets(file_path: str):
    """Concatenates tweets in a file.

    Args:
        file_path (str): path to where the contexts are stored

    Returns:
        Generator: a generator with the concatenated tweets
    """
    context_tweets: List[str] = []
    for context in ndjson_gen(file_path):
        concatenated = concat_context(context)
        context_tweets.append(concatenated)

    return context_tweets


def extract_save_triplets(
    responses: dict,
    template: PromptTemplate,
    event: str,
    nlp: spacy.Language,
):
    subjects, predicates, objects, triplets = [], [], [], []
    for response in responses["choices"]:
        for triplet in template.parse_prompt(response["text"], target_tweet=""):
            if "" in (triplet.subject, triplet.predicate, triplet.object):
                continue
            subject = nlp(triplet.subject)._.most_common_ancestor.text
            predicate = nlp(triplet.predicate)._.most_common_ancestor.text
            obj = nlp(triplet.object)._.most_common_ancestor.text
            subjects.append(subject)
            predicates.append(predicate)
            objects.append(obj)
            triplets.append(f"{subject}, {predicate}, {obj}")

    write_txt(
        os.path.join("extracted_triplets_tweets", event, "subjects.txt"),
        subjects,
        "a+",
    )
    write_txt(
        os.path.join("extracted_triplets_tweets", event, "predicates.txt"),
        predicates,
        "a+",
    )
    write_txt(
        os.path.join("extracted_triplets_tweets", event, "objects.txt"),
        objects,
        "a+",
    )
    write_txt(
        os.path.join("extracted_triplets_tweets", event, "triplets.txt"),
        triplets,
        "a+",
    )


def main(
    file_path: str,
    event: str,
    api_key: str,
    template_batch_size: int = 20,
    sample_size: Union[None, int] = None,
    org_id: Optional[str] = None,
):
    """Main function for extracting triplets from tweets Uses GPT3 prompting.

    Args:
        file_path (str): path to where the contexts are stored
        event (str): name of the event. Used when saving the extracted triplets
        template_batch_size (int, optional): Number of tweets to prompt GPT3 with at a time.
            Defaults to 20 (max length for list of prompts).
    """
    # Check if the folder for the event exists, if not create it
    Path(os.path.join("extracted_triplets_tweets", event)).mkdir(
        parents=True,
        exist_ok=True,
    )
    print("Loading gold docs and setting up template")
    template = prepare_template(MarkdownPromptTemplate2)
    print("Concatenating tweets")
    concatenated = concatenate_tweets(file_path)

    # Downsampling
    if sample_size:
        if len(concatenated) < sample_size:
            print(
                f"Sample size ({sample_size}) is larger than the number of tweets ({len(concatenated)}), using all tweets",
            )
        else:
            concatenated = random.sample(concatenated, sample_size)
            print(f"Downsampled to {len(concatenated)} tweets")

    # Setup
    coref_nlp = build_coref_pipeline()
    head_nlp = build_headword_extraction_pipeline()
    if org_id:
        openai.org_id = org_id
    openai.api_key = api_key

    print("batching")
    for i, batch in enumerate(batch_generator(concatenated, template_batch_size)):
        start = time.time()
        coref_docs = coref_nlp.pipe(batch)
        resolved_docs = (d._.resolve_coref for d in coref_docs)
        resolved_target_tweets = (
            tweet_from_context_text(tweet) for tweet in resolved_docs
        )
        prompts = [
            template.create_prompt(target=tweet) for tweet in resolved_target_tweets
        ]

        print(f"sending request for batch {i}")
        while True:
            try:
                responses = openai.Completion.create(
                    model="text-davinci-002",
                    prompt=prompts,
                    temperature=0.7,
                    max_tokens=500,
                )

                print("parsing response and saving")
                extract_save_triplets(responses, template, event, head_nlp)
                print(f"batch {i} done in {time.time() - start} seconds\n")
                break

            except openai.error.InvalidRequestError as e:
                print("Invalid request got error: ", e)
                print("Retrying with fewer examples...")
                # Randomly select an example to drop
                current_examples: List[Doc] = list(template.examples)
                current_examples.pop(random.randrange(len(current_examples)))
                template.set_examples(current_examples)  # type: ignore
                prompts = [
                    template.create_prompt(target=tweet)
                    for tweet in resolved_target_tweets
                ]

            except openai.error.APIConnectionError:
                print("Connection reset, waiting 20 sec then retrying...")
                time.sleep(20)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--file_path",
        type=str,
        help="Path to the file containing the context tweets",
    )
    parser.add_argument(
        "-e",
        "--event",
        type=str,
        help="Name of the event. Used when saving the extracted triplets",
    )
    parser.add_argument(
        "-t",
        "--template_batch_size",
        type=int,
        default=20,
        required=False,
        help="Number of tweets to prompt GPT3 with at a time. Defaults to 20 (max length for list of prompts).",
    )
    parser.add_argument(
        "-s",
        "--sample_size",
        type=int,
        default=30000,
        required=False,
        help="Number of tweets to downsample dataset to. Defaults to 30000.",
    )
    parser.add_argument(
        "-o",
        "--org_id",
        type=str,
        required=False,
        default=None,
        help="OpenAI organization ID",
    )
    parser.add_argument(
        "-api_key",
        "--api_key",
        type=str,
        help="OpenAI API key",
    )
    # file_path = os.path.join("src", "TESTnew_tweet_threads_2019-03-10_2019-03-17.ndjson")
    # event="covid_week_1"
    # template_batch_size=20
    args = parser.parse_args()
    main(
        file_path=args.file_path,
        event=args.event,
        api_key=args.api_key,
        template_batch_size=args.template_batch_size,
        sample_size=args.sample_size,
        org_id=args.org_id,
    )
