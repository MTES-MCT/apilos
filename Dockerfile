# syntax=docker/dockerfile:1
FROM python:3.10.4
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code/
RUN rm -rf .venv
RUN pip install pipenv
RUN pipenv install
