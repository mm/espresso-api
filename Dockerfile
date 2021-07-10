FROM python:3.9.1-slim-buster

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends libpq-dev gcc python3-dev \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pipenv && pipenv install --system

RUN useradd --create-home espresso
USER espresso
WORKDIR /home/espresso
COPY . .