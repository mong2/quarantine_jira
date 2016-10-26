FROM alpine:3.4
MAINTAINER awilson@cloudpassage.com

RUN apk update && \
    apk add \
    gcc \
    musl-dev \
    python \
    python-dev \
    py-pip

COPY target-events /conf/target-events
COPY app/ /app/
COPY requirements.txt /etc/requirements.txt

RUN pip install -r /etc/requirements.txt

CMD python /app/runner.py
