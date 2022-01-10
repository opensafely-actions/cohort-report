""" Command line tool for using cohort reporter """
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from cohortreport import __version__
from cohortreport.report import make_report
from cohortreport.utils import load_config


def run_action(input_files: List, config: Dict) -> None:
    """
    Takes each input file in turn and creates the HTML graphs for each
    variable as per the configuration.

    Args:
        input_files: The input files from which the graphs are created.
        config: The configuration as a JSON object or str
    """

    for input_file in input_files:
        make_report(
            path=Path(input_file),
            output_dir=config["output_path"],
            variable_types=config["variable_types"],
        )


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

    # run cohort report
    run_action(input_files=args.input_files, config=processed_config)


if __name__ == "__main__":
    main()
