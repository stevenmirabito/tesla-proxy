FROM python:3.7
MAINTAINER Steven Mirabito <stevenmirabito@gmail.com>

COPY . /opt/tesla-proxy
WORKDIR /opt/tesla-proxy

RUN pip install pipenv && \
    pipenv lock --requirements > requirements.txt && \
    pipenv --rm && \
    pip uninstall --yes pipenv && \
    pip install -r requirements.txt

ENV PYTHONUNBUFFERED=TRUE

CMD gunicorn --bind=0.0.0.0:8080 --capture-output tesla_proxy:app

