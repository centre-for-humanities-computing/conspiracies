import argparse


from conspiracies.pipeline.config import PipelineConfig
from conspiracies.pipeline.pipeline import Pipeline


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "project_name",
        nargs="?",
        default=None,
    )
    arg_parser.add_argument(
        "input_path",
        nargs="?",
        default=None,
    )
    arg_parser.add_argument(
        "-c",
        "--config",
        default="config/default.toml",
    )
    args = arg_parser.parse_args()

    cli_args = {
        "base.project_name": args.project_name,
        "preprocessing.input_path": args.input_path,
    }
    config = PipelineConfig.from_toml_file(args.config, cli_args)

    pipeline = Pipeline(config)
    pipeline.run()
