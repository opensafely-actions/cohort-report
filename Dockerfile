# syntax=docker/dockerfile:1.2
FROM ghcr.io/opensafely-core/python:latest 

# labeling
LABEL org.opencontainers.image.title="cohortreport" \
      org.opencontainers.image.description="Cohort Report action for opensafely.org" \
      org.opencontainers.image.source="https://github.com/opensafely-core/cohort-report-action" \
      org.opensafely.action="cohortreport"

# re-use entrypoint from base-docker image
ENV ACTION_EXEC=cohortreport

# local install
RUN --mount=type=bind,target=/src python -m pip install /src
