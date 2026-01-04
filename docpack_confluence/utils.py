# -*- coding: utf-8 -*-

from pathlib import Path


def extract_id(url_or_id: str) -> str:
    """
    Extract the page ID from a Confluence URL or return the ID if directly provided.

    This function handles different Confluence URL formats and extracts the page ID.
    It also handles cases where the URL has a trailing /* or when just the ID is provided.

    :param url_or_id: A Confluence page URL or direct page ID.
        Example: "https://example.atlassian.net/wiki/spaces/BD/pages/123456/Value+Proposition"
        or just "123456"

    :return: The extracted page ID as a string
    """
    # If it's just an ID (possibly with /* at the end)
    if "/" not in url_or_id or url_or_id.count("/") == 1 and url_or_id.endswith("/*"):
        # Remove /* if present
        return url_or_id.rstrip("/*")

    # It's a URL, extract the ID which comes after /pages/ segment
    parts = url_or_id.split("/pages/")
    if len(parts) != 2:
        raise ValueError(f"Invalid Confluence URL format: {url_or_id}")

    # The ID is the segment after /pages/ and before the next /
    id_and_title = parts[1].split("/", 1)
    return id_and_title[0]


def process_include_exclude(
    include: list[str],
    exclude: list[str],
) -> tuple[list[str], list[str]]:
    """
    Process include and exclude patterns for Confluence page IDs or URLs.

    This function takes lists of include and exclude patterns that might be
    Confluence page URLs or IDs, extracts the page IDs from them, and preserves
    any trailing wildcards (/*). It normalizes all inputs to a consistent format
    of either just the ID or ID with wildcard.

    :param include: List of Confluence page URLs or IDs to include
        Items can be full URLs, page IDs, or patterns with /* suffix
    :param exclude: List of Confluence page URLs or IDs to exclude
        Items can be full URLs, page IDs, or patterns with /* suffix

    :return: A tuple of two lists:
        1. Normalized include patterns with extracted IDs
        2. Normalized exclude patterns with extracted IDs
    """
    new_include, new_exclude = list(), list()
    for expr in include:
        id = extract_id(expr)
        if expr.endswith("/*"):
            new_include.append(id + "/*")
        else:
            new_include.append(id)
    for expr in exclude:
        id = extract_id(expr)
        if expr.endswith("/*"):
            new_exclude.append(id + "/*")
        else:
            new_exclude.append(id)
    return new_include, new_exclude


def safe_write(path: Path, content: str):
    try:
        path.write_text(content, encoding="utf-8")
    except FileNotFoundError:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
