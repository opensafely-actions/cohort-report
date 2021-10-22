""" Command line tool for using cohort reporter """
import argparse
import json
from pathlib import Path
from typing import Dict, List

from cohortreport import __version__
from cohortreport.report import make_report
from cohortreport.utils import load_config


def convert_config(file_or_string: str) -> Dict:
    """
    Takes in a JSON string or a path to a JSON file and outputs
    the config as Python object such as a dict
    Args:
        file_or_string:
    Returns:
        Configuration as loaded JSON
    """
    path = Path(file_or_string)
    try:
        if path.exists():
            with path.open() as f:
                config = json.load(f)
        else:
            config = json.loads(file_or_string)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"Could not parse {file_or_string}\n{exc}")

    return config


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


def main():
    """
    Command line tool for running cohort report.
    """

    # make args parser
    parser = argparse.ArgumentParser(
        description="Outputs variable report and graphs from cohort"
    )

    # configurations
    parser.add_argument(
        "--config",
        help="Configuration as either a JSON str or a path to a JSON file",
    )

    # version
    parser.add_argument(
        "--version", action="version", version=f"cohortreport {__version__}"
    )

    # input files
    parser.add_argument(
        "input_files", nargs="*", help="Files that cohort report will be run on"
    )

    # parse args
    args = parser.parse_args()

    # convert config path to config dict
    config_dict = convert_config(args.config)
    processed_config = load_config(config_dict)

    # run cohort report
    run_action(input_files=args.input_files, config=processed_config)


if __name__ == "__main__":
    main()
