FROM python:3.13.12-slim-trixie AS builder

RUN ["pip", "install", "requests==2.32.5"]
RUN ["pip", "install", "beautifulsoup4==4.14.3"]
RUN ["mkdir", "db"]

ENV PYTHONPATH="/src"

WORKDIR /src
COPY ./src/common common
COPY ./src/data data
COPY .env .env


FROM builder AS debug

RUN apt-get -y update && apt-get install -y --no-install-recommends \
    fzf \
		neovim \
		sqlite3 \
		tree \
	; \
	rm -rf /var/lib/apt/lists/*;

RUN ["pip", "install", "harlequin"]

ENTRYPOINT ["/bin/sh"]


FROM builder AS prod

RUN ["pip", "install", "python-dotenv"]

RUN useradd --create-home --shell /bin/bash appuser

USER appuser


ENTRYPOINT ["python", "data/main.py"]
