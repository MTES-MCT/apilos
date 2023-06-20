# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONUNBUFFERED=1
ARG IPYTHON_AUTORELOAD

# clamav is used in celery to scan uploads before after they reach the file system
RUN apt update
RUN apt install clamav -y

WORKDIR /code
COPY requirements.txt .
COPY dev-requirements.txt .

# pip ugrade & pip tools install
RUN pip install --upgrade pip # Pip upgrade
RUN pip install pip-tools

SHELL ["/bin/bash", "-c"]

RUN pip install -r requirements.txt -r dev-requirements.txt

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
