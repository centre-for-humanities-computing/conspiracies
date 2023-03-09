import os
import openai
import random
import argparse
from extract import extract_spacy_examples

from conspiracies.prompt_relation_extraction.template_class import (
    PromptTemplate1,
    PromptTemplate2,
    MarkdownPromptTemplate1,
    MarkdownPromptTemplate2,
    XMLStylePromptTemplate,
)
from conspiracies.data import load_gold_triplets
from typing import List, Optional, Tuple
from spacy.tokens import Doc
from conspiracies.prompt_relation_extraction.data_classes import SpanTriplet


def get_paths(machine: str, get_openai_key: Optional[bool] = False):
    """Returns appropriate path depending on machine.

    Args:
        machine (str): current machine. Specialized to 'grundtvig' or 'ucloud'
        get_openai_key (bool, optional): Whether or not to return the open ai key. Defaults to False.
    Returns:
        root_path (str): path to where data is stored
        prediction_path (str): path to where predictions should be saved
        openai_key (str, optional): the key for accessing open ai. Only returned if get_openai_key is True
    """
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
            "/work",
            "conspiracies",
            "data",
            "triplet-extraction-gpt",
        )
        prediction_path = os.path.join(root_path, "predictions")
        with open(os.path.join("/work", "conspiracies", "openai_API_key.txt")) as f:
            openai_key = f.read()

    else:
        root_path = os.getcwd()
        openai_key = "key"
        prediction_path = root_path
        print(
            f'Invalid machine, using current path ({root_path}) and the openai key "{openai_key}"',
        )

    if get_openai_key:
        return root_path, prediction_path, openai_key
    else:
        return root_path, prediction_path


def get_introduction_text(html_tagged: Optional[bool] = False) -> str:
    if html_tagged:
        text = """Tag the following tweet with triplets using HTML tags.
Semantic triplets consists of the elements subject, verb phrase and object. The verb phrase includes all particles and modifyers.
There should always be exactly three elements in a triplet, no more no less.
The subject is enclosed between <subject-n> and </subject-n>, the verb phrase between <predicate-n> and </predicate-n> and the object between <object-n> and </object-n>.
n is the number of the triplet, starting at 1. Elements of one triplet can be contained within elements of another triplet.
The triplets should be tagged in the tweet as shown below:"""
    else:
        text = """Extract semantic triplets from the following tweet. 
The semantic triplets should be on the form (Subject - Verb Phrase - Object), where the verb phrase includes all particles and modifyers. 
There should always be exactly three elements in a triplet, no more no less. 
They should be put in a markdown table as shown below:"""
    return text


def get_prompt_functions(templates: Optional[List[int]] = None):
    """Returns a dictionary with specified prompt template functions.

    If no
    templates is specified, all available are returned.
    Args:
        templates (List[int], optional): templates to include in the dict
    Returns:
        template_dicts (dict): dictionary with string of template name as key and the function as value
    """
    template_dicts = {
        "template1": PromptTemplate1,
        "template2": PromptTemplate2,
        "template3": MarkdownPromptTemplate1,
        "template4": MarkdownPromptTemplate2,
        "template5": XMLStylePromptTemplate,
    }
    if templates is None:
        return template_dicts
    else:
        return {f"template{i}": template_dicts[f"template{i}"] for i in templates}


def return_example_tuple(
    examples: List[dict],
) -> Tuple[List[Doc], List[List[SpanTriplet]]]:
    """Returns a tuple of example tweets and their corresponding triplets
    Args:
        examples (List[dict]): list of dictionaries with tweet and triplets
    Returns:
        example_tweets (List[str]): list of example tweets
        example_triplets (List[List[str]]): list of example triplets
    """
    example_tweets = [tweet["doc"] for tweet in examples]
    example_triplets = [tweet["triplets"] for tweet in examples]
    return example_tweets, example_triplets


def run_triplet_extraction2(
    data: Tuple[List[dict], List[dict]],
    machine: str,
    templates: List[int],
    openai_key: str,
    iteration: int,
) -> None:
    root_path, prediction_path = get_paths(machine)
    targets, examples = data
    example_tweets, example_triplets = return_example_tuple(examples)

    # docs_to_jsonl(
    #     example_tweets,
    #     example_triplets,
    #     os.path.join(prediction_path, f"spacy_examples_set_{iteration}.json"),
    # )
    dict_functions = get_prompt_functions(templates)
    for key, value in dict_functions.items():
        print(f"Prompting using {key}\n")
        gpt_outputs = []
        html_tagged = True if key == "template5" else False
        template = value(
            examples=return_example_tuple(examples),
            task_description=get_introduction_text(html_tagged=html_tagged),
        )

        while True:
            try:
                for tweet in targets:
                    openai.api_key = openai_key
                    response = openai.Completion.create(
                        model="text-davinci-002",
                        prompt=template.create_prompt(tweet["doc"].text),
                        temperature=0.7,
                        max_tokens=500,
                    )

                    gpt_outputs.append(response["choices"][0]["text"])
                break
            except openai.error.InvalidRequestError:
                examples.pop(random.randrange(len(examples)))
                print(f"Too many examples, trying {len(examples)} examples")
                template.set_examples(return_example_tuple(examples))
                continue

        # docs_to_jsonl(
        #     [target["doc"] for target in targets],
        #     [parse(pred) for pred in gpt_outputs],
        #     os.path.join(prediction_path, f"{key}_gpt_spacy_{iteration}.json"),
        # )


def main2(
    machine: str,
    n_target: int,
    templates: List[int],
    iterations: int,
) -> None:
    root_path, prediction_path, openai_key = get_paths(machine, get_openai_key=True)
    docs, triplets = load_gold_triplets()
    data = [{"doc": doc, "triplets": triplets} for doc, triplets in zip(docs, triplets)]

    assert (
        len(data) / n_target >= iterations
    ), f"Cannot extract {n_target} target tweets per iteration with {iterations} iterations and {len(data)} tweets"

    print(f"Running {iterations} iterations with {n_target} tweets per iteration")

    # targets and examples will contain cross-validated extracted examples
    targets, examples = extract_spacy_examples(data, n_target, iterations)
    # print("Targets and examples extracted")
    # print(type(targets[0][0]))
    # print(targets[0])
    # print(type(examples[0][0]))

    for i in range(iterations):
        print(f"Iteration {i}")
        run_triplet_extraction2(
            (targets[i], examples[i]),
            machine,
            templates,
            openai_key,
            i,
        )


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
