import argparse
import json
import pathlib
import sys

from cohortreport import __version__
from cohortreport.report import make_report
from cohortreport.utils import load_config


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="Cohort Report outputs graphs of variables in a study input file"
    )
    parser.add_argument(
        "--config", type=json.loads, help="A JSON string that contains configuration"
    )
    parser.add_argument(
        "--version", action="version", version=f"cohortreport {__version__}"
    )
    parser.add_argument("input_files", nargs="*", help="Study input files")
    return parser.parse_args(args)


def main():
    args = parse_args(sys.argv[1:])

    processed_config = load_config(args.config if args.config is not None else {})

    for input_file in args.input_files:
        make_report(
            path=pathlib.Path(input_file),
            output_dir=processed_config["output_path"],
            variable_types=processed_config["variable_types"],
        )


if __name__ == "__main__":
    main()
