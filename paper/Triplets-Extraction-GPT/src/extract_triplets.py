"""Main script for extracting triplets using GPT3."""

import os
import openai
import json
from extract import extract_examples
from create_templates import (
    prompt_template_1,
    prompt_template_2,
    prompt_template_3,
    prompt_template_4,
)
from typing import List
import argparse


def create_list_dics(tweet, triplets):
    result = {}
    result["tweet"] = tweet
    result["triplets"] = triplets
    return result


def get_all_prompt_functions():
    return {
        "template1": prompt_template_1,
        "template2": prompt_template_2,
        "template3": prompt_template_3,
        "template4": prompt_template_4,
    }


def run_triplet_extraction(
    data: List[dict],
    prediction_path: str,
    n_tweets: int,
    dict_functions: dict,
    openai_key: str,
    iteration: int,
):

    print(f"Running function with {n_tweets} tweets")
    examples, target_tweets = extract_examples(data, n_tweets)

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
        for tweet in target_tweets:
            template = value(
                examples=examples,
                target_tweet=tweet,
                introduction="""Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three phrases extracted, no more no less. 
They should be put in a markdown table as shown below:""",
            )
            # print("Template used:\n\n")
            # print(template)
            # print("\n\n")
            openai.api_key = openai_key
            response = openai.Completion.create(
                model="text-davinci-002",
                prompt=template,
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


def main(
    machine: str,
    n_tweets: int,
    templates: List[int],
    iterations: int,
):

    # Preparing paths, files and folders
    if machine == "grundtvig":
        root_path = os.path.join("/data", "conspiracies", "triplet-extraction-gpt")
        prediction_path = os.path.join(
            "/home",
            os.getlogin(),
            "data",
            "predictions",
        )
        with open(os.path.join("/home", os.getlogin(), "openai_API_key.txt")) as f:
            openai_key = f.read()
    elif machine == "ucloud":
        root_path = os.path.join(
            "/work", "conspiracies", "data", "triplet-extraction-gpt"
        )
        prediction_path = os.path.join(root_path, "predictions")
        with open(os.path.join("/work", "conspiracies", "openai_API_key.txt")) as f:
            openai_key = f.read()
    else:
        root_path = os.getcwd()
        openai_key = "key"
        prediction_path = root_path
        print(
            f'Invalid machine, using current path ({root_path}) and the openai key "{openai_key}"'
        )

    with open(
        os.path.join(root_path, "tagged", "tagged_tweets_with_features.json"),
        "r",
        encoding="utf8",
    ) as f:
        data = json.load(f)

    all_dicts = get_all_prompt_functions()
    dict_functions = {f"template{i}": all_dicts[f"template{i}"] for i in templates}

    # Looping over triplet extraction, exception for too long prompt decreases n example tweets
    for i in range(iterations):
        print(f"Iteration {i}")

        while True:
            try:
                run_triplet_extraction(
                    data, prediction_path, n_tweets, dict_functions, openai_key, i
                )
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
        "--n_tweets",
        default=20,
        type=int,
        help="Number of example tweets to use if possible",
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

    main(args.machine, args.n_tweets, args.templates, args.iterations)
