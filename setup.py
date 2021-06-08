from setuptools import find_namespace_packages, setup

from cohortreport.version import __version__


setup(
    name="cohort-report-action",
    version=__version__,
    packages=find_namespace_packages(exclude=["tests"]),
    include_package_data=True,
    url="https://github.com/opensafely-core/cohort-report-action",
    description="Command line tool for graphing study cohorts",
    long_description="Command line tool for creating graphs and tables describing "
    "a study cohort variables (univariates only).",
    license="GPLv3",
    author="OpenSAFELY",
    author_email="tech@opensafely.org",
    python_requires=">=3.7",
    install_requires=["pandas", "plotly", "pyarrow", "jinja2"],
    entry_points={"console_scripts": ["cohortreport=cohortreport.__main__:main"]},
    classifiers=["License :: OSI Approved :: GNU General Public License v3 (GPLv3)"],
)
