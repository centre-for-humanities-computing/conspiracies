from typing import List

from spacy.language import Language
from spacy_transformers.layers.transformer_model import huggingface_tokenize

from transformers import PreTrainedTokenizer


def wordpiece_length_normalization(
    texts: List[str],
    nlp: Language,
    tokenizer: PreTrainedTokenizer,
    max_length: int = 500,
):
    """Yield a list of text split into subtext which respect the maximum
    wordpiece or sentencepiece tokens (max_length).

    Args:
        texts: (List[str]): List of strings.
        nlp (Language): A spacy Language pipeline
        tokenizer (str): The pretrained transformer tokenizer.
        max_length (int): The maximum number of tokens of the model. Defualt to 500.

    Example:
        >>> import spacy
        >>> from transformers import AutoTokenizer
        >>> nlp = spacy.load("da_core_news_lg")
        >>> short_texts = ["hello there"]
        >>> tokenizer_name = "DaNLP/da-bert-tone-subjective-objective"
        >>> tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        >>> norm_text = wordpiece_length_normalization(short_texts, nlp, tokenizer)
        >>> list(norm_text)  # short texts should result in the same output
        ["hello there"]
    """

    def __wordpiece_length(text: str):
        wp_tokens = huggingface_tokenize(tokenizer, [text])
        return len(wp_tokens["input_ids"][0])

    def __split_sentence(sent):
        nonlocal min_span

        doc = sent.doc
        max_span = sent.start + 1
        while max_span < sent.end:
            span_wp_length = __wordpiece_length(doc[min_span:max_span].text)
            if span_wp_length > max_length:
                if min_span + 1 == max_span:
                    raise ValueError(
                        "The following token span consist"
                        + f" of more than {max_length} word pieces.",
                    )
                yield doc[min_span:max_span].text
                min_span = max_span
            max_span += 1
        # yield remaining sentence
        if min_span < sent.end:
            yield doc[min_span : sent.end].text
        min_span = sent.end + 1

    docs = nlp.pipe(texts)
    for doc in docs:
        doc_wp_length = __wordpiece_length(doc.text)

        if doc_wp_length < max_length:
            yield doc.text
        else:  # if doc needs to be split
            min_span = 0

            for sent in doc.sents:
                span_wp_length = __wordpiece_length(doc[min_span : sent.end].text)

                if span_wp_length > max_length:
                    if min_span == sent.start:
                        # if the sentence is too long split it to longest possible
                        # substring respecting token bounderies.
                        for sub_sent in __split_sentence(sent):
                            yield sub_sent
                    # if too long yield up until sentence
                    else:
                        yield doc[min_span : sent.start].text
                        min_span = sent.start

            if min_span < sent.end:
                yield doc[min_span : sent.end].text  # yield remaining sentence
