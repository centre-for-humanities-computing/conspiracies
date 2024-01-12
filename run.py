import argparse
import glob
import json
import os


from conspiracies.docprocessing.docprocessor import DocProcessor
from conspiracies.document import Document
from conspiracies.preprocessing.tweets import TweetsPreprocessor


def iter_lines_of_files(glob_pattern: str):
    files = glob.glob(glob_pattern, recursive=True)
    for file in files:
        with open(file) as f:
            for line in f:
                yield line


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("project_name")
    arg_parser.add_argument("input_path")
    arg_parser.add_argument(
        "--n_cores",
        default=os.cpu_count(),
    )
    args = arg_parser.parse_args()

    preprocessor = TweetsPreprocessor(args.project_name, n_cores=args.n_cores)

    preprocessor.preprocess_docs(args.input_path)

    doc_processor = DocProcessor()

    doc_processor.process_docs(
        (
            json.loads(line, object_hook=Document)
            for line in iter_lines_of_files(f"output/{args.project_name}/part*.ndjson")
        ),
        f"output/{args.project_name}/annotations.ndjson",
    )
