FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED = 1

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app/

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip install -r requirements.txt


COPY . /app/