##
## Dockerfile for Webex Desk Pro Call Status to MQTT
##
FROM python:3.12.8-slim-bullseye AS base
FROM base AS build-image

RUN apt update
RUN apt install --no-install-recommends -y build-essential gcc libffi-dev
EXPOSE 5001
HEALTHCHECK CMD curl --fail http://localhost:5001/healthcheck || exit 1

WORKDIR /app

RUN pip install poetry
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt | /venv/bin/pip install -r /dev/stdin
COPY . .
#RUN poetry build && /venv/bin/pip install dist/*.whl

FROM base AS final

COPY --from=build-image /venv /venv
COPY docker-entrypoint.sh src/webexstatus/status.py /app/
CMD ["/app/docker-entrypoint.sh"]
