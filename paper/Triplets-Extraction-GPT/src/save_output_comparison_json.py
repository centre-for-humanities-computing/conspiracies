import json
import os
from typing import List
import argparse
from utils import (
    find_tweet_in_list_of_dicts,
    get_paths,
    get_triplet_from_string,
    write_triplets,
    sanity_check_triplets
)

def main(
    machine: str,
    templates: List[int],
    iterations: int,
    sanity_check:bool=True
):
    root_path, prediction_path = get_paths(machine)
    out_file = os.path.join(prediction_path, "gpt_predictions_compare.json")

    list_of_tweet_dicts = []
    for i in range(iterations):
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
            tweet_dict = {}
            tweet = d["tweet"]
            triplets = get_triplet_from_string(d["triplets"])
            gold_dict = find_tweet_in_list_of_dicts(tweet, input_data, "resolved")

            tweet_dict["tweet"] = tweet
            tweet_dict["gold_tagging"] = gold_dict["triplets"]
            if sanity_check:
                tweet_dict[f"template_{first}"] = sanity_check_triplets(triplets)
            else: 
                tweet_dict[f"template_{first}"] = triplets

            for n in templates[1:]:
                new_file = os.path.join(
                    prediction_path,
                    f"template{n}_gpt_outputs_{i}.json",
                )

                with open(new_file, "r") as f:
                    data = json.load(f)
                new_dict = find_tweet_in_list_of_dicts(tweet, data)
                new_triplets = get_triplet_from_string(new_dict["triplets"])
                if sanity_check:
                    tweet_dict[f"template_{n}"] = sanity_check_triplets(new_triplets)
                else:
                    tweet_dict[f"template_{n}"] = new_triplets
            list_of_tweet_dicts.append(tweet_dict)

    with open(out_file, "w") as f:
        json.dump(list_of_tweet_dicts, f, indent=2)


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
    parser.add_argument(
        "-s",
        "--sanity_check",
        default=True,
        type=bool,
        help="Whether or not to sanity check the tweets before saving. Defaults to true"
    )
    args = parser.parse_args()

    main(args.machine, args.templates, args.iterations, args.sanity_check)
