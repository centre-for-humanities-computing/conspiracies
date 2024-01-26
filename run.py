import argparse
import os


from conspiracies.pipeline.config import (
    ProjectConfig,
    PreprocessingConfig,
    DocprocessingConfig,
)
from conspiracies.pipeline.runner import Runner


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("project_name")
    arg_parser.add_argument("input_path")
    arg_parser.add_argument(
        "--n_cores",
        default=os.cpu_count(),
    )
    args = arg_parser.parse_args()

    runner = Runner()
    runner.project_config = ProjectConfig(
        project_name=args.project_name,
        output_root="output",
        language="da",
    )
    runner.preprocessing_config = PreprocessingConfig(
        input_path=args.input_path,
        doc_type="tweets",
    )
    runner.docprocessing_config = DocprocessingConfig(
        triplet_extraction_method="multi2oie",
    )

    runner.preprocessing()
    runner.docprocessing()
    runner.corpusprocessing()
