# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.10.9
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY Pipfile Pipfile.lock wait-for-it.sh /app/
RUN pip install pipenv && pipenv install --system --deploy --ignore-pipfile && chmod +x wait-for-it.sh

USER appuser

COPY . .

ENTRYPOINT ["./wait-for-it.sh", "zephyrzen-database:3306", "--", "python", "-m", "bot"]
