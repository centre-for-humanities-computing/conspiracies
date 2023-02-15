import json
import os
from typing import List
from collections import Counter
import argparse
from utils import (
    find_tweet_in_list_of_dicts,
    get_paths,
    get_triplet_from_string,
    write_triplets,
)


def main(
    machine: str,
    templates: List[int],
    iterations: int,
):
    root_path, prediction_path = get_paths(machine)
    out_file = os.path.join(prediction_path, "prompt_outputs_compare_templates.md")
    counters = {f"Template {t}": Counter({f"extraction_errors": 0}) for t in templates}

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
            root_path,
            "tagged",
            "tagged_tweets_with_features.json",
        )

        with open(first_file, "r") as f:
            first_data = json.load(f)
        with open(gold_file, "r") as f:
            input_data = json.load(f)

        for d in first_data:
            tweet = d["tweet"]
            triplets = get_triplet_from_string(d["triplets"])

            gold_dict = find_tweet_in_list_of_dicts(tweet, input_data, "resolved")
            input_text = f"\n\n#### Target tweet:\n{tweet}\n\n"
            header = (
                "| Type | Subject | Predicate | Object |\n| --- | --- | --- | --- |\n"
            )

            with open(out_file, "a") as f:
                f.write(input_text)
                f.write(header)

            write_triplets(gold_dict["triplets"], out_file, "Gold")
            write_triplets(
                triplets, out_file, f"Template {first}", counters[f"Template {first}"]
            )

            for n in templates[1:]:
                new_file = os.path.join(
                    prediction_path,
                    f"template{n}_gpt_outputs_{i}.json",
                )

                with open(new_file, "r") as f:
                    data = json.load(f)
                new_dict = find_tweet_in_list_of_dicts(tweet, data)
                triplets = get_triplet_from_string(new_dict["triplets"])
                write_triplets(
                    triplets, out_file, f"Template {n}", counters[f"Template {n}"]
                )

    for template, counter in counters.items():
        with open(out_file, "a") as f:
            f.write(
                f'\n\n #### {template} had {counter["extraction_errors"]} extraction errors'
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

    main(args.machine, args.templates, args.iterations)
