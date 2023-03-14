# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONUNBUFFERED=1
ARG IPYTHON_AUTORELOAD

WORKDIR /code
COPY requirements.txt .
COPY dev-requirements.txt .

# pip ugrade & pip tools install
RUN pip install --upgrade pip # Pip upgrade
RUN pip install pip-tools

SHELL ["/bin/bash", "-c"]

RUN pip install -r requirements.txt -r dev-requirements.txt

#CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "--timeout", "30", "core.wsgi:application", "--reload"]
