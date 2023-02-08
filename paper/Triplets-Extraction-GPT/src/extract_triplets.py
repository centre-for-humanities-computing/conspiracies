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


def create_list_dics(tweet, triplets):
    result = {}
    result["tweet"] = tweet
    result["triplets"] = triplets
    return result


root_path = os.path.join("/work", "conspiracies", "data", "triplet-extraction-gpt")
with open(
    os.path.join(root_path, "tagged", "tagged_tweets_with_features.json"),
    "r",
    encoding="utf8",
) as f:
    data = json.load(f)
with open(os.path.join("/work", "conspiracies", "openai_API_key.txt")) as f:
    openai_key = f.read()


dict_functions = {
    #   "template1": prompt_template_1,
    #   "template2": prompt_template_2,
    "template3": prompt_template_3,
    "template4": prompt_template_4,
}

for i in range(2):
    examples, target_tweets = extract_examples(data, 9)

    examples_set = []
    for tweet, triplet in examples:
        examples_dict = create_list_dics(tweet, triplet)
        examples_set.append(examples_dict)

    examples_json = json.dumps(examples_set, ensure_ascii=False, indent=2)

    with open(
        os.path.join(root_path, "predictions", f"examples_set_{i}.json"), "w"
    ) as outfile:
        outfile.write(examples_json)

    for key, value in dict_functions.items():
        print(f"Using {key}\n")

        gpt_outputs = []
        for tweet in target_tweets:
            template = value(
                examples=examples,
                target_tweet=tweet,
                introduction="Extract semantic triples from the following tweets and put them in the form (Subject)(VerbPhrase)(Arg):",
            )
            print("Template used:\n\n")
            print(template)
            print("\n\n")
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
            os.path.join(root_path, "predictions", f"{key}_gpt_outputs_{i}.json"), "w"
        ) as outfile:
            outfile.write(outputs_json)
