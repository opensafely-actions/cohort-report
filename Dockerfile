# Grab the docker python image
FROM ghcr.io/opensafely-core/python:latest as base-python

# Upgrade pip and cohort report
RUN python -m pip install -U pip setuptools wheel

# local install
COPY ./ ./
RUN python -m pip install .

# labeling
LABEL org.opencontainers.image.title="report" \
      org.opencontainers.image.description="Cohort Report action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/cohort-report-action" \
      org.opensafely.action="report"

# re-use entrypoint from base-docker image
ENV ACTION_EXEC=report