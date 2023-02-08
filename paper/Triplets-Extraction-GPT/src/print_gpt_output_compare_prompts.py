import json
import os
from typing import List
import argparse


def find_tweet_in_list_of_dicts(tweet, dict_list):
    for d in dict_list:
        if d["tweet"] == tweet:
            return d


def get_header(template_number, tweet):
    if template_number == 3:
        return f"| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |\n|{tweet}|"
    else:
        return "| Subject | Predicate | Object |\n| --- | --- | --- |\n"


def main(
    machine: str,
    print_in_terminal: bool,
    templates: List[int],
    iterations: int,
):
    if machine == "grundtvig":
        root_path = os.path.join("/data", "conspiracies", "triplet-extraction-gpt")
        prediction_path = os.path.join(
            "/home",
            os.getlogin(),
            "data",
            "predictions",
        )
    elif machine == "ucloud":
        root_path = os.path.join(
            "/work", "conspiracies", "data", "triplet-extraction-gpt"
        )
        prediction_path = os.path.join(root_path, "predictions")
    else:
        root_path = os.getcwd()
        prediction_path = root_path
        print(f'Invalid machine, using current path ({root_path})"')

    out_file = os.path.join(prediction_path, "prompt_outputs_compare_templates.txt")

    with open(out_file, "w") as f:
        f.write("Comparing templates:\n")
        for n in templates:
            f.write(f"\t{n}\n")

    for i in range(iterations):
        with open(out_file, "a") as f:
            f.write(f"\n### Examples set {i}\n")
        first = templates[0]
        first_file = os.path.join(
            prediction_path,
            f"template{first}_gpt_outputs_{i}.json",
        )
        gold_file = os.path.join(
            root_path, "tagged", "tagged_tweets_with_features.json"
        )

        with open(first_file, "r") as f:
            first_data = json.load(f)

        with open(gold_file, "r") as f:
            input_data = json.load(f)

        for d in first_data:
            tweet = d["tweet"]
            gold_dict = find_tweet_in_list_of_dicts(tweet, input_data)
            input_text = f"\n\n#### Target tweet:\n{tweet}\n\n##### Gold:\n"
            gold_header = get_header(0, tweet)  # Any number but 3
            first_header = get_header(first, tweet)

            if print_in_terminal:
                print(input_text)
                print(gold_header)
            with open(out_file, "a") as f:
                f.write(input_text)
                f.write(gold_header)

            for triplet in gold_dict["triplets"]:
                triplet_string = f"|{triplet[0]}|{triplet[1]}|{triplet[2]}|\n"
                with open(out_file, "a") as f:
                    f.write(triplet_string)

            with open(out_file, "a") as f:
                f.write(f"\n##### Template {first}:\n")
                f.write(first_header)
                f.write(d["triplets"])

            if print_in_terminal:
                print(f"\n\nTemplate {first}:\n")
                print(first_header, d["triplets"])

            for n in templates[1:]:
                new_file = os.path.join(
                    prediction_path,
                    f"template{n}_gpt_outputs_{i}.json",
                )
                n_header = get_header(n, tweet)
                with open(new_file, "r") as f:
                    data = json.load(f)
                new_dict = find_tweet_in_list_of_dicts(tweet, data)
                with open(out_file, "a") as f:
                    f.write(f"\n\n##### Template {n}:\n")
                    f.write(n_header)
                    f.write(new_dict["triplets"])

                if print_in_terminal:
                    print(f"\nTemplate {n}:\n")
                    print(n_header)
                    print(new_dict["triplets"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m",
        "--machine",
        type=str,
        help='Which machine are you working on? Takes values "grundtvig" or "ucloud',
    )
    parser.add_argument(
        "-p",
        "--print_terminal",
        default=False,
        type=bool,
        help="Whether or not to also print directly to console",
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

    main(args.machine, args.print_terminal, args.templates, args.iterations)
