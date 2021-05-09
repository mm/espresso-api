FROM python:3.9.0-slim-buster AS base

WORKDIR /readlater
COPY . .
RUN pip install pipenv \
    && apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev \
    && pipenv install --system \
    && apt-get --purge -y remove libpq-dev gcc python3-dev \
    && apt autoremove -y