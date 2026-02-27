FROM python:3.13.12-slim-bookworm
# AS builder

RUN ["pip", "install", "requests==2.32.5"]
RUN ["pip", "install", "beautifulsoup4==4.14.3"]
RUN ["mkdir", "db"]

ENV PYTHONPATH="/src"

WORKDIR /src
COPY ./src/common common
COPY ./src/data data

ENTRYPOINT ["python", "data/mensa-data.py"]

# FROM python:3.13.12-slim-bookworm AS prod
