# syntax=docker/dockerfile:1
FROM python:3.10.4
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY . /code/
<<<<<<< HEAD
SHELL ["/bin/bash", "-c"]
RUN source .venv/bin/activate
RUN pip install -r requirements.txt
=======
RUN rm -rf .venv
RUN pip install pipenv
RUN pipenv install
>>>>>>> ea4a9c1 (manage menu)
