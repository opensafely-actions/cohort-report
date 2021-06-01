
# Grab the docker python base image
FROM ghcr.io/opensafely-core/base-docker:latest as base-python

# Virtual envir
RUN python3 -m venv

# Copy requirements and install
COPY requirements.txt requirements.txt
RUN python -m pip install -U pip setuptools wheel && \
    python -m pip install --requirement requirements.txt

# Build Python image from base python
FROM base-python as report

LABEL org.opencontainers.image.title="report" \
      org.opencontainers.image.description="Cohort Report action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/cohort-report-action" \
      org.opensafely.action="report"

RUN mkdir /workspace
WORKDIR /workspace