

from cohort_report.processing import load_study_cohort

def test_load_study_cohort():
    """ tests that study cohort is loaded correctly"""
    test_df = load_study_cohort(path='tests/test_data/input.csv')
