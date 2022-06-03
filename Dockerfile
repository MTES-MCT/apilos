# syntax=docker/dockerfile:1
FROM python:3.10.4
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code/
SHELL ["/bin/bash", "-c"]
RUN source .venv/bin/activate
RUN pip install -r requirements.txt
