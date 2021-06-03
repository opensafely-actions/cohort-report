""" Command line tool for using cohort reporter """
from cohort_report.report import make_report
from utils_entrypoint import load_config

import argparse
import json
from pathlib import Path
import os

from version import __version__

class ActionConfig:


    def __init__(self, validator=None):
        self.validator = validator

    def __call__(self, file_or_string):
        path = Path(file_or_string)
        try:
            if path.exists():
                with path.open() as f:
                    config = json.load(f)
            else:
                config = json.loads(file_or_string)
        except json.JSONDecodeError as exc:
            raise argparse.ArgumentTypeError(f"Could not parse {file_or_string}\n{exc}")

        if self.validator:
            try:
                self.validator(config)
            except Exception as exc:
                raise argparse.ArgumentTypeError(f"Invalid action config:\n{exc}")

        return config

    @classmethod
    def add_to_parser(cls, parser, help="The configuration for the cohort report", validator=None):
        parser.add_argument(
            "--config",
            required=True,
            help=help,
            type=ActionConfig(validator),
        )


def load_cohort_report(input_files: list, config: dict) -> None:

    processed_config = load_config(config)

    for input_file in input_files:
        input_filename_with_ext = os.path.basename(input_file)
        input_filename = os.path.splitext(input_filename_with_ext)[0]
        make_report(
                path=Path(input_file),
                output_dir=processed_config["output_path"],
                input_file_name=input_filename,
                variable_types=processed_config["variable_types"],
            )


def main():
    """
    Command line tool for running cohort report.
    """
    # make args parser
    parser = argparse.ArgumentParser(
        description="Outputs variable report and graphs from cohort"
    )

    # add configuration arg
    ActionConfig.add_to_parser(parser)

    # version
    parser.add_argument("--version", action="version", version=f"cohortreport {__version__}")

    # input files
    parser.add_argument("input_files", nargs="*", help="Files that cohort report will be run on")

    # parse args
    args = parser.parse_args()

    # run cohort report
    load_cohort_report(
        input_files=args.input_files, config=args.config
    )


if __name__ == "__main__":
    main()
