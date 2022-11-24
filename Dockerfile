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

# Install ipython & setup autoreload, if required
RUN echo "${IPYTHON_AUTORELOAD}"
RUN if [ -n "${IPYTHON_AUTORELOAD}" ]; then pip install ipython; fi
RUN if [ -n "${IPYTHON_AUTORELOAD}" ]; then ipython profile create; fi
RUN if [ -n "${IPYTHON_AUTORELOAD}" ]; then echo "c.InteractiveShellApp.exec_lines = []" > ~/.ipython/profile_default/ipython_config.py; fi
RUN if [ -n "${IPYTHON_AUTORELOAD}" ]; then echo "c.InteractiveShellApp.exec_lines.append('%load_ext autoreload')" >> ~/.ipython/profile_default/ipython_config.py; fi
RUN if [ -n "${IPYTHON_AUTORELOAD}" ]; then echo "c.InteractiveShellApp.exec_lines.append('%autoreload 2')" >> ~/.ipython/profile_default/ipython_config.py; fi

SHELL ["/bin/bash", "-c"]

RUN pip install -r requirements.txt -r dev-requirements.txt

CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
