# -*- coding: utf-8 -*-

"""
Playground test for crawl_descendants.

Parses entity titles to validate:
- Title prefix ('p'/'f') matches node type (page/folder)
- Level in title (L{n}) matches lineage depth
"""

import re

from docpack_confluence.crawler import (
    crawl_descendants,
    crawl_descendants_with_cache,
)
from docpack_confluence.constants import DescendantTypeEnum
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import homepage_id
from docpack_confluence.one import one


# Title format: "{type}{number}-L{level}"
# Examples: "p01-L1", "f04-L4", "p77-L12"
TITLE_PATTERN = re.compile(r"^([pf])(\d+)-L(\d+)$")


def parse_title(title: str) -> tuple[str, int, int] | None:
    """
    Parse entity title to extract type, number, and level.

    :param title: Title like "p01-L1" or "f04-L4"
    :returns: Tuple of (type_prefix, number, level) or None if no match
    """
    match = TITLE_PATTERN.match(title)
    if not match:
        return None
    type_prefix = match.group(1)  # 'p' or 'f'
    number = int(match.group(2))  # e.g., 1, 4, 77
    level = int(match.group(3))  # e.g., 1, 4, 12
    return type_prefix, number, level


def test():
    """
    Test crawl_descendants by validating parsed title against entity properties.

    Validates:
    1. Title prefix matches node type ('p' -> page, 'f' -> folder)
    2. Level in title matches lineage length (depth from root)
    """
    print("\n" + "=" * 60)
    print("Test: Validate entity title vs properties")
    print("=" * 60)

    entities = crawl_descendants_with_cache(
        client=client,
        root_id=homepage_id,
        root_type=DescendantTypeEnum.page,
        cache=one.cache,
    )

    print(f"\nTotal entities: {len(entities)}")

    # Expected type mapping
    type_map = {"p": "page", "f": "folder"}

    # Track stats
    pages_count = 0
    folders_count = 0
    max_level = 0

    for entity in entities:
        title = entity.node.title
        parsed = parse_title(title)

        if parsed is None:
            print(f"  WARNING: Cannot parse title: {title}")
            continue

        type_prefix, number, level = parsed

        # Assert 1: Type prefix matches node type
        expected_type = type_map[type_prefix]
        actual_type = entity.node.type
        assert actual_type == expected_type, (
            f"Type mismatch for {title}: expected '{expected_type}', got '{actual_type}'"
        )

        # Assert 2: Level matches lineage length
        actual_level = len(entity.lineage)
        assert actual_level == level, (
            f"Level mismatch for {title}: expected {level}, got {actual_level}"
        )

        # Track stats
        if type_prefix == "p":
            pages_count += 1
        elif type_prefix == "f":
            folders_count += 1
        else:
            pass
        max_level = max(max_level, level)

    print(f"\nValidation passed for all {len(entities)} entities:")
    print(f"  - Pages: {pages_count}")
    print(f"  - Folders: {folders_count}")
    print(f"  - Max level: {max_level}")
    print("\nPASSED: All entity titles match their properties")


if __name__ == "__main__":
    from docpack_confluence.tests import run_unit_test

    run_unit_test(__file__)
