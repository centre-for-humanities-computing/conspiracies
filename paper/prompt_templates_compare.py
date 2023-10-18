from data import load_api_key
import spacy
from data import load_gold_triplets
from extract_examples import extract_examples
from spacy.training import Example


def save_string(path, text_string, method="w"):
    with open(path, method) as f:
        f.write(text_string)


def create_pipeline(
    template: str,
    n_target: int = 10,
    cv: int = 2,
):
    nlp = spacy.load("da_core_news_trf")
    gold_docs = load_gold_triplets(nlp=nlp)
    targets, examples = extract_examples(gold_docs, n_target, cv)
    if template == "chatgpt_style_template":
        model_name = "gpt-3.5-turbo"
        backend = "conspiracies/openai_chatgpt_api"
    else:
        model_name = "text-davinci-002"
        backend = "conspiracies/openai_gpt3_api"
    config = {
        "prompt_template": f"conspiracies/{template}",
        "examples": None,
        "task_description": None,
        "model_name": model_name,
        "backend": backend,
        "api_key": load_api_key(),
        "split_doc_fn": None,
        "api_kwargs": {
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        },
        "force": True,
    }
    relation_component = nlp.add_pipe(
        "conspiracies/prompt_relation_extraction",
        last=True,
        config=config,
    )

    for cv, (target_set, example_set) in enumerate(zip(targets, examples)):
        prompt_template = relation_component.prompt_template
        prompt_template.examples = example_set
        docs = nlp.pipe([doc.text for doc in target_set])
        docs = list(docs)
        predictions = [
            Example(predicted=pred_doc, reference=gold_doc)
            for pred_doc, gold_doc in zip(docs, target_set)
        ]
        scores = relation_component.score(predictions)
        print(f"Scores for round {cv} using template {template}:")
        scores.pop("sample_scores")
        print(scores)
        row = f'|{template} {cv+1} | {scores["exact_span_match_f1"]} | {scores["exact_string_match_f1"]} | {scores["normalized_span_overlap_f1"]} | {scores["normalized_string_overlap_f1"]} | {scores["n_predictions"]} | {scores["n_references"]} |\n'
        save_string("results.md", row, "a")


templates = [
    # "template_1",
    # "template_2",
    # "markdown_template_1",
    # "markdown_template_2",
    # "xml_style_template",
    "chatgpt_style_template",
]
header = """
Socring: 
|Template CV | exact span match f1 | exact string match f1 | norm span overlap f1 | norm string overlap f1 | n predictions | n references |
| --- | --- | --- | --- | --- | --- | --- |
"""

# save_string("results.md", header)
for template in templates:
    create_pipeline(template)
