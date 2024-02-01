import argparse


from conspiracies.pipeline.config import PipelineConfig
from conspiracies.pipeline.pipeline import Pipeline


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "project_name",
        nargs="?",
        default=None,
        help="Name of your project under which various output files will be output"
        "under output root set in config (the default for which is output/).",
    )
    arg_parser.add_argument(
        "input_path",
        nargs="?",
        default=None,
        help="Input path for preprocessing of documents. Can be a glob path, e.g."
        "path/to/files/*.txt. Be mindful of quotes for glob paths.",
    )
    arg_parser.add_argument(
        "-c",
        "--config",
        default="config/default.toml",
        help="Path to configuration file. Refer to config/template.toml for contents.",
    )
    args = arg_parser.parse_args()

    cli_args = {
        "base.project_name": args.project_name,
        "preprocessing.input_path": args.input_path,
    }
    config = PipelineConfig.from_toml_file(args.config, cli_args)

    pipeline = Pipeline(config)
    pipeline.run()
