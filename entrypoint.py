""" Command line tool for using cohort reporter """
import argparse
import json
from pathlib import Path

from cohort_report.report import make_report
from utils_entrypoint import load_config


def load_cohort_report(input_files, config) -> None:

    processed_config = load_config(config)

    for input_name, path in input_files.items():
        make_report(
            path=Path(path),
            output_dir=processed_config["output_path"],
            input_file_name=input_name,
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

    # version
    parser.add_argument("--version", action="version", version="cohortreport 0.0.1")

    # configurations
    parser.add_argument("config", type=str, help="XXX add something here")

    # parse args
    args = parser.parse_args()

    kwargs = vars(args)

    json_path = kwargs.pop("config")

    with open(json_path) as json_file:
        instructions = json.load(json_file)
        if "config" not in instructions:
            raise KeyError("config not defined in instructions")
        if "inputs" not in instructions:
            raise KeyError("input not defined in instructions")

    # run cohort report
    load_cohort_report(
        input_files=instructions["inputs"], config=instructions["config"]
    )


if __name__ == "__main__":
    main()
