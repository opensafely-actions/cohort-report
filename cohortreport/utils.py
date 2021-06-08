from typing import Dict

DEFAULTS = {"output_path": "cohort_reports_outputs/", "variable_types": None}


def load_config(config) -> Dict:
    """
    Takes in cohort report configuration and changes these key-value pairs
    where indicated by the cohort report config. All other key-value pairs
    are left as default values

    Args:
        config (dict): dictionary of the cohort report configuration
            taken from json

    Returns:
        Dict (cfg): Configuration dictionary to be passed to entry point.
    """
    cfg = DEFAULTS.copy()
    cfg.update(config)
    return cfg
