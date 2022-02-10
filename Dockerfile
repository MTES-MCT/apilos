# syntax=docker/dockerfile:1
FROM python:3.10.1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code/
RUN pip install pipenv
RUN pipenv install
