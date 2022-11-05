# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt .
COPY dev-requirements.txt .

SHELL ["/bin/bash", "-c"]

RUN pip install -r requirements.txt -r dev-requirements.txt

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
