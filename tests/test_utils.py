from cohortreport.utils import load_config


class TestLoadConfig:
    def test_updated_correctly(self):
        test_config = {"output_path": "test_path", "variable_types": "test_typing"}

        observed_config = load_config(test_config)
        assert observed_config["output_path"] == "test_path"
        assert observed_config["variable_types"] == "test_typing"

    def test_partially_updated(self):
        test_config = {"output_path": "test_path"}

        observed_config = load_config(test_config)

        assert observed_config["output_path"] == "test_path"
        assert observed_config["variable_types"] == None

    def test_defaults_only(self):
        test_config = {}

        observed_config = load_config(test_config)

        assert observed_config["output_path"] == "cohort_reports_outputs/"
        assert observed_config["variable_types"] == None
