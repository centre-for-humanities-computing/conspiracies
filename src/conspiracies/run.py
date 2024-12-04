import argparse
import logging

from conspiracies.pipeline.config import PipelineConfig
from conspiracies.pipeline.pipeline import Pipeline


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "output_path",
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
        "--language",
        "-l",
        default=None,
        help="Language of models and word lists.",
    )
    arg_parser.add_argument(
        "--n_docs",
        "-n",
        default=None,
        help="Max number of documents to output from preprocessing.",
    )
    arg_parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="Path to configuration file. Refer to config/template.toml for contents.",
    )
    arg_parser.add_argument(
        "--root-log-level",
        default="WARN",
        help="Level of root logger.",
    )
    args = arg_parser.parse_args()

    logging.getLogger().setLevel(args.root_log_level)

    cli_args = {
        "base.output_path": args.output_path,
        "base.language": args.language,
        "preprocessing.input_path": args.input_path,
        "preprocessing.n_docs": args.n_docs,
    }

    if args.config:
        config = PipelineConfig.from_toml_file(args.config, cli_args)
    else:
        config = PipelineConfig.default_with_extra_config(cli_args)

    pipeline = Pipeline(config)

    logging.basicConfig(
        level=logging.DEBUG,
        filename=config.base.output_path + "/logfile",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filemode="a+",
    )
    logging.info("Running pipeline...")

    pipeline.run()
