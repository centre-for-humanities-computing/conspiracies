from spacy.tokens import Span
import time
import os
from pathlib import Path
from typing import List, Generator
import spacy
from transformers import AutoTokenizer
import argparse

# Conspiracies
from conspiracies.preproc import wordpiece_length_normalization
from extract_utils import load_ndjson, write_txt


def build_coref_pipeline():
    nlp_coref = spacy.blank("da")
    nlp_coref.add_pipe("sentencizer")
    nlp_coref.add_pipe("allennlp_coref")

    return nlp_coref


def yield_one_article(articles: List[dict]) -> Generator:
    for article in articles:
        yield article["text"]


def exclude_newspapers(
    files: List[str],
    papers_to_exclude: List[str] = ["weekendavisen"],
) -> List[str]:
    """Excludes newspapers from file list
    Args:
        file_list (List[str]): list of files
        papers_to_exclude (List[str]): list of newspapers to exclude
    Returns:
        file_list (List[str]): list of files without excluded newspapers
    """
    file_list = [
        file for file in files if not any(paper in file for paper in papers_to_exclude)
    ]
    return file_list


nlp_for_normalization = spacy.load("da_core_news_sm")
tokenizer = AutoTokenizer.from_pretrained("vesteinn/DanskBERT")


def process_file(
    file: str,
    event: str,
    norm_nlp=nlp_for_normalization,
    tokenizer=tokenizer,
):
    start = time.time()
    data: List[dict] = load_ndjson(file)

    # Create pipeline to resolve coreference
    spacy.prefer_gpu()
    nlp_coref = spacy.blank("da")
    nlp_coref.add_pipe("sentencizer")
    nlp_coref.add_pipe("allennlp_coref")

    # Create pipeline to extract relations
    nlp = spacy.load("da_core_news_sm")
    nlp.add_pipe("sentencizer")
    nlp.add_pipe(
        "heads_extraction",
        config={"normalize_to_entity": True, "normalize_to_noun_chunk": True},
    )
    config = {"confidence_threshold": 2.7, "model_args": {"batch_size": 10}}
    nlp.add_pipe("relation_extractor", config=config)

    for i, article in enumerate(yield_one_article(data)):
        normalized_article = list(
            wordpiece_length_normalization(
                [article],
                norm_nlp,
                tokenizer,
                max_length=500,
            ),
        )
        if i % 10 == 0:
            print(f"Now processing article {i}/{len(data)}")

        # Resolve coreference
        coref_docs = nlp_coref.pipe(normalized_article)
        resolved_docs = (d._.resolve_coref for d in coref_docs)

        # Extract relations
        docs = nlp.pipe(resolved_docs)

        # Extract triplets and write to file
        subjects, predicates, objects, triplets = [], [], [], []
        for doc in docs:
            for triplet in doc._.relation_triplets:
                if not all(isinstance(element, Span) for element in triplet):
                    continue
                if len(triplet) != 3:
                    continue
                subject = triplet[0]._.most_common_ancestor.text
                predicate = triplet[1]._.most_common_ancestor.text
                object = triplet[2]._.most_common_ancestor.text
                subjects.append(subject)
                predicates.append(predicate)
                objects.append(object)
                triplets.append((subject, predicate, object))
        if len(triplets) == 0:
            continue
        write_txt(
            os.path.join("extracted_triplets_papers", event, "subjects.txt"),
            subjects,
            "a+",
        )
        write_txt(
            os.path.join("extracted_triplets_papers", event, "predicates.txt"),
            predicates,
            "a+",
        )
        write_txt(
            os.path.join("extracted_triplets_papers", event, "objects.txt"),
            objects,
            "a+",
        )
        write_txt(
            os.path.join("extracted_triplets_papers", event, "triplets.txt"),
            triplets,
            "a+",
        )
    write_txt(
        os.path.join("extracted_triplets_papers", event, "processed_files.txt"),
        [file],
        "a+",
    )
    print(f"Finished piping {file} in {time.time() - start} seconds")


def main(event: str, papers_to_exclude: List[str]):
    event_path = os.path.join(
        "/home",
        os.getlogin(),
        "narratives-political-events",
        "data",
        "clean_news",
        event,
    )
    Path(os.path.join("extracted_triplets_papers", event)).mkdir(
        parents=True,
        exist_ok=True,
    )
    start = time.time()
    files = os.listdir(event_path)
    # Do not look at articles from specified papers. Default is weekendavisen
    files = exclude_newspapers(files, papers_to_exclude)
    print("starting processing all articles")
    for file_n, file in enumerate(files):
        print(
            f"\n__________________________________________\nNow processing {file} ({file_n+1}/{len(files)})",
        )
        file_path = os.path.join(event_path, file)
        process_file(file_path, event)

    print(
        f"Finished processing all articles in {time.time() - start} seconds. Now writing to file",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-e",
        "--event",
        type=str,
        help="Name of the event to run triplet extraction on",
    )
    parser.add_argument(
        "-ex",
        "--exclude",
        type=str,
        nargs="+",
        default=["weekendavisen"],
        help="Newspapers to exclude from the extraction",
    )

    args = parser.parse_args()
    main_start = time.time()
    main(args.event, args.exclude)
