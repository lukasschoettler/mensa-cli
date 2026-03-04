FROM python:3.13.12-slim-bookworm AS builder

RUN ["pip", "install", "requests==2.32.5"]
RUN ["pip", "install", "beautifulsoup4==4.14.3"]
RUN ["mkdir", "db"]

ENV PYTHONPATH="/src"

WORKDIR /src
COPY ./src/common common
COPY ./src/data data


FROM builder AS debug

RUN apt-get install -y --no-install-recommends \
		sqlite3 \
    lazysql \
		tree \
		nvim \
    fzf \
	; \
	rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/bin/sh"]


FROM builder AS prod

ENTRYPOINT ["python", "data/mensa-data.py"]
