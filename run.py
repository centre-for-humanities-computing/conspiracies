import argparse
import os


from conspiracies.pipeline.config import (
    ProjectConfig,
    PreprocessingConfig,
    DocprocessingConfig,
    PipelineConfig,
)
from conspiracies.pipeline.pipeline import Pipeline


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--project_name",
        required=False,
    )
    arg_parser.add_argument(
        "--input_path",
        required=False,
    )
    arg_parser.add_argument(
        "--n_cores",
        default=os.cpu_count(),
    )
    arg_parser.add_argument(
        "-c",
        "--config",
        required=False,
    )
    args = arg_parser.parse_args()

    if args.config:
        pipeline = Pipeline(config=PipelineConfig.from_toml_file(args.config))
    else:
        raise NotImplementedError("Construction site. Sorry!")
        pipeline = Pipeline(config=PipelineConfig())
        pipeline.project_config = ProjectConfig(
            project_name=args.project_name,
            output_root="output",
            language="da",
        )
        pipeline.preprocessing_config = PreprocessingConfig(
            input_path=args.input_path,
            doc_type="tweets",
        )
        pipeline.docprocessing_config = DocprocessingConfig(
            triplet_extraction_method="multi2oie",
        )

    pipeline.preprocessing()
    pipeline.docprocessing(continue_from_last=True)
    pipeline.corpusprocessing()
