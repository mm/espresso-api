FROM python:3.9

WORKDIR /readlater

RUN pip install pipenv
COPY . .

RUN pipenv install --system