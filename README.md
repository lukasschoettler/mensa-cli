This Repo contains two things:

- A CLI to check todays menu of your mensa
- An attempt at building a database containing mensa menus

This project is just for me to learn some stuff.

# Mensa CLI

A CLI tool which scrapes today's menu of your Mensa. Currently supports Mensas which are part of the "Studierendenwerk Berlin".

## Installation

Install directly from source using the project metadata defined in `pyproject.toml`:

```bash
pip install -e .
```

This installs the `mensa` console entry point.

## Usage

```bash

# comes with built-in help
mensa --help

# List available mensas
mensa list

# Scrape a menu of your mensa
mensa scrape -m <mensa_key>
```

# Mensa Data

The data part of this project aims to eventually build a database containing the mensa menus, using the scrapers originally written for the CLI.
As of now, there's nothing functional here.

## Build and run

```bash
# In this repo
docker build . --no-cache --target prod -t mensa-data

# The debug build target comes with shell utilities to make debugging simpler.
docker build . --no-cache --target debug -t mensa-data-debug

# This mounts the empty "db" directory into the container, which is used for the sqlite3 database. This way the database can be inspected outside of the container
docker run --mount type=bind,src=./db,dst=/src/db mensa-data

docker run -it --mount type=bind,src=./db,dst=/src/db mensa-data-debug
```
