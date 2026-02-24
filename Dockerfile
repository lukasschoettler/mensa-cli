FROM python:3.13.12-bookworm
# AS builder

WORKDIR /app

COPY mensa-data.py /app

ENTRYPOINT ["python", "mensa-data.py"]

# FROM python:3.13.12-slim-bookworm AS prod
