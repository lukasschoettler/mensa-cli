"""HTTP utilities for fetching Mensa pages."""
from __future__ import annotations

import logging
from typing import Mapping, Optional
from urllib.parse import quote, urlsplit, urlunsplit

import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS: Mapping[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
}


def normalize_url(url: str) -> str:
    """Percent-encode path and query components for stability."""
    parts = urlsplit(url)
    path = quote(parts.path)
    query = quote(parts.query, safe="=&")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def fetch_html(
    url: str,
    *,
    session: Optional[requests.Session] = None,
    headers: Optional[Mapping[str, str]] = None,
    timeout: int = 10,
) -> str:
    """Fetch HTML content from the given URL using provided session/settings."""
    normalized = normalize_url(url)
    client = session or requests

    logger.debug("Fetching URL %s", normalized)
    response = client.get(normalized, timeout=timeout, headers=headers or DEFAULT_HEADERS)
    response.raise_for_status()
    return response.text
