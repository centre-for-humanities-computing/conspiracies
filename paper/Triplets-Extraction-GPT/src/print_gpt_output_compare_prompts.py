import json
import os


def find_tweet_in_list_of_dicts(tweet, dict_list):
    for d in dict_list:
        if d["tweet"] == tweet:
            return d


def get_header(template_number, tweet):
    if template_number == 3:
        return f"| Tweet | Subject | Predicate | Object |\n| --- | --- | --- | --- |\n|{tweet}|"
    else:
        return "| Subject | Predicate | Object |\n| --- | --- | --- |\n"


root_path = os.path.join("/work", "conspiracies", "data", "triplet-extraction-gpt")
template_numbers = [3, 4]
out_file = "prompt_outputs_compare_templates.txt"

with open(out_file, "w") as f:
    f.write("Comparing templates:\n")
    for n in template_numbers:
        f.write(f"\t{n}\n")


for i in range(2):  # This should really be automized
    with open(out_file, "a") as f:
        f.write(f"\n### Examples set {i}\n")
    first = template_numbers[0]
    first_file = os.path.join(
        root_path, "predictions", f"template{first}_gpt_outputs_{i}.json"
    )
    gold_file = os.path.join(root_path, "tagged", "tagged_tweets_with_features.json")

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
        print(f"\n\nTemplate {first}:\n")
        print(first_header, d["triplets"])

        for n in template_numbers[1:]:
            file = os.path.join(
                root_path, "predictions", f"template{n}_gpt_outputs_{i}.json"
            )
            n_header = get_header(n, tweet)
            with open(file, "r") as f:
                data = json.load(f)
            new_dict = find_tweet_in_list_of_dicts(tweet, data)
            with open(out_file, "a") as f:
                f.write(f"\n\n##### Template {n}:\n")
                f.write(n_header)
                f.write(new_dict["triplets"])
            print(f"\nTemplate {n}:\n")
            print(n_header)
            print(new_dict["triplets"])
