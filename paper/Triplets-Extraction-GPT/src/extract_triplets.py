"""Main script for extracting triplets using GPT3."""

import os
import openai
import json
import spacy
import random
from extract import extract_examples, extract_spacy_examples
from create_templates import (
    prompt_template_1,
    prompt_template_2,
    prompt_template_3,
    prompt_template_4,
)
from conspiracies.prompt_relation_extraction.template_class import (
    PromptTemplate1,
    PromptTemplate2,
    PromptTemplate3,
    PromptTemplate4,
    PromptTemplate5,
)
from typing import List, Optional, Union
import argparse
from utils import get_introduction_text, get_paths
from conspiracies import docs_from_jsonl, docs_to_jsonl, parse


def create_list_dics(tweet: str, triplets: Optional[List[list]]) -> dict:
    """Takes a tweet and associated triplets (if any is given) and combines to
    a dict.

    Args:
        tweet (str): the tweet from wich triplets are extracted
        triplets (Optional[List[list]]): list of list(s) of triplets OR None if no triplets are in the tweet

    Returns:
        dict: a dictionary with the tweet and the triplets on the form
            {"tweet": tweet,
            "triplets": List[list] | None}
    """
    result = {}
    result["tweet"] = tweet
    result["triplets"] = triplets
    return result


def get_prompt_functions(templates: Optional[List[int]] = None):
    """Returns a dictionary with specified prompt template functions. If no
    templates is specified, all available are returned.

    Args:
        templates (List[int], optional): templates to include in the dict

    Returns:
        template_dicts (dict): dictionary with string of template name as key and the function as value
    """
    template_dicts = {
        "template1": PromptTemplate1,
        "template2": PromptTemplate2,
        "template3": PromptTemplate3,
        "template4": PromptTemplate4,
        "template5": PromptTemplate5,
    }
    if templates is None:
        return template_dicts
    else:
        return {f"template{i}": template_dicts[f"template{i}"] for i in templates}


def run_triplet_extraction2(
    data: List[dict],
    machine: str,
    dict_functions: dict,
    openai_key: str,
    iteration: int,
) -> List[str]:

    root_path, prediction_path = get_paths(machine)
    targets, examples = data

    docs_to_jsonl(
        [tweet["doc"] for tweet in examples],
        [tweet["triplets"] for tweet in examples],
        os.path.join(prediction_path, f"spacy_examples_set_{iteration}.json"),
    )

    for key, value in dict_functions.items():
        print(f"Prompting using {key}\n")
        gpt_outputs = []
        html_tagged = True if key == "template5" else False
        template = value(
            examples=examples,
            task_description=get_introduction_text(html_tagged=html_tagged),
        )

        print(template.generate_prompt(targets[0]["doc"].text))
        # while True:
        #     try:
        #         for tweet in targets:
        #             openai.api_key = openai_key
        #             response = openai.Completion.create(
        #                 model="text-davinci-002",
        #                 prompt=template.generate_prompt(tweet["doc"].text),
        #                 temperature=0.7,
        #                 max_tokens=500,
        #             )
        #             ### How to parse the output back to spacy?? ask kenneth
        #             # print(parse(response["choices"][0]["text"]))
        #             # print(parse(response["choices"][0]["text"])["triplets"])
        #             # print(type(parse(response["choices"][0]["text"])["triplets"]["1"]["subject"]))

        #             gpt_outputs.append(response["choices"][0]["text"])
        #         break
        #     except openai.error.InvalidRequestError:
        #         examples.pop(random.randrange(len(examples)))
        #         print(f"Too many examples, trying {len(examples)} examples")
        #         template.set_examples(examples)
        #         continue

        docs_to_jsonl(
            [target["doc"] for target in targets],
            [parse(pred) for pred in gpt_outputs],
            os.path.join(prediction_path, f"{key}_gpt_spacy_{iteration}.json"),
        )


def main2(
    machine: str,
    n_target: int,
    templates: List[int],
    iterations: int,
) -> None:

    root_path, prediction_path, openai_key = get_paths(machine, get_openai_key=True)
    nlp = spacy.blank("da")
    path_to_data = os.path.join(
        "/home",
        os.getlogin(),
        "conspiracies",
        "data",
        "gold_triplets.jsonl",
    )
    docs, triplets = docs_from_jsonl(path_to_data, nlp)
    data = [{"doc": doc, "triplets": triplets} for doc, triplets in zip(docs, triplets)]

    assert (
        len(data) / n_target >= iterations
    ), f"Cannot extract {n_target} target tweets per iteration with {iterations} iterations and {len(data)} tweets"

    print(f"Running {iterations} iterations with {n_target} tweets per iteration")

    # targets and examples will contain cross-validated extracted examples
    targets, examples = extract_spacy_examples(data, n_target, iterations)

    for i in range(iterations):
        print(f"Iteration {i}")
        run_triplet_extraction2(
            (targets[i], examples[i]),
            machine,
            templates,
            openai_key,
            i,
        )


def run_triplet_extraction(
    data: List[dict],
    machine: str,
    n_tweets: int,
    dict_functions: dict,
    openai_key: str,
    iteration: int,
    prev_target_tweets: Optional[List[str]] = None,
) -> List[str]:
    """Runs one iteration of triplet extraction given a set of example tweets
    Writes example set with the iteration number and file with prompt outpus to
    the prediction_path.

    Args:
        data (List[dict]): list of dicts containing tweets and tagged triplets
        machine (str): current machine - are you on ucloud or grundtvig?
        n_tweets (int): number of tweets to use as examples. The rest will be used as target tweets
        dict_functions (dict): dictionary with template extraction functions to use
        openai_key (str): key to accessing openai API
        iteration (int): current iteration number

    Returns:
        target_tweets (List[str]): list of the tweets used as target/validation tweets
    """
    print(f"Running function with {n_tweets} tweets")

    root_path, prediction_path = get_paths(machine)

    examples, target_tweets = extract_examples(data, n_tweets, prev_target_tweets)

    examples_set = []
    for tweet, triplet in examples:
        examples_dict = create_list_dics(tweet, triplet)
        examples_set.append(examples_dict)

    examples_json = json.dumps(examples_set, ensure_ascii=False, indent=2)

    with open(
        os.path.join(
            prediction_path,
            f"examples_set_{iteration}.json",
        ),
        "w",
    ) as outfile:
        outfile.write(examples_json)

    for key, value in dict_functions.items():
        print(f"Prompting using {key}\n")

        gpt_outputs = []
        # Creating an instance of the template class
        template = value(examples=examples, task_description=get_introduction_text())

        for tweet in target_tweets:

            openai.api_key = openai_key
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=template.generate_prompt(tweet),
                temperature=0.7,
                max_tokens=500,
            )

            result = create_list_dics(tweet, response["choices"][0]["text"])
            gpt_outputs.append(result)
        outputs_json = json.dumps(gpt_outputs, ensure_ascii=False, indent=2)

        with open(
            os.path.join(
                prediction_path,
                f"{key}_gpt_outputs_{iteration}.json",
            ),
            "w",
        ) as outfile:
            outfile.write(outputs_json)
    return target_tweets


def main(
    machine: str,
    n_tweets: int,
    templates: List[int],
    iterations: int,
) -> None:
    """Runs iterations iterations of the triplet extraction. Uses all templates
    specified. Tries to use n_tweets example tweets, but decreases number if
    that means prompt becomes too long.

    Args:
        machine (str): current machine - are you on ucloud or grundtvig?
        n_tweets (int): number of tweets to use as examples
        templates (List[int]): list of template number to use
        iterations (int): number of iterations for each template

    Returns:
        None
    """

    # Preparing paths, files and folders
    root_path, prediction_path, openai_key = get_paths(machine, get_openai_key=True)

    with open(
        os.path.join(root_path, "tagged", "tagged_tweets_with_features.json"),
        "r",
        encoding="utf8",
    ) as f:
        data = json.load(f)

    dict_functions = get_prompt_functions(templates)

    # Looping over triplet extraction, exception for too long prompt decreases n example tweets
    prev_target_tweets = None
    for i in range(iterations):
        print(f"Iteration {i+1}")

        while True:
            try:
                if not prev_target_tweets:
                    print("Prev target tweets is none")
                    prev_target_tweets = run_triplet_extraction(
                        data,
                        machine,
                        n_tweets,
                        dict_functions,
                        openai_key,
                        i,
                        prev_target_tweets,
                    )
                else:
                    new_target_tweets = run_triplet_extraction(
                        data,
                        machine,
                        n_tweets,
                        dict_functions,
                        openai_key,
                        i,
                        prev_target_tweets,
                    )
                    prev_target_tweets += new_target_tweets
                break
            except openai.error.InvalidRequestError:
                n_tweets -= 1
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--machine",
        type=str,
        help='Which machine are you working on? Takes values "grundtvig" or "ucloud',
    )
    parser.add_argument(
        "-n",
        "--n_target_tweets",
        default=10,
        type=int,
        help="Number of target tweets to use if possible",
    )
    parser.add_argument(
        "-t",
        "--templates",
        nargs="+",
        type=int,
        help="Integers indicating templates to use",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        default=2,
        type=int,
        help="Number of iterations of sampling and prompting",
    )

    args = parser.parse_args()

    main2(args.machine, args.n_target_tweets, args.templates, args.iterations)
