FROM python:3.13.12-bookworm
# AS builder

WORKDIR /app

COPY ./src/data /app
COPY ./src/common /app

RUN ["mkdir", "db"]

ENTRYPOINT ["python", "mensa-data.py"]

# FROM python:3.13.12-slim-bookworm AS prod
