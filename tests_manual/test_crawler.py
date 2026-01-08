# -*- coding: utf-8 -*-

"""
Consolidated test for crawl_descendants_with_cache.

Fetches entities once and validates everything in a single loop:
- Total count, pages count, folders count
- Title prefix matches node type
- Level in title matches lineage depth
- Entities sorted by position_path
- Lineage structure (self is first)
- Path properties consistency
"""

import re

from docpack_confluence.crawler import crawl_descendants_with_cache
from docpack_confluence.constants import DescendantTypeEnum
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import homepage_id
from docpack_confluence.one import one


# Expected values
EXPECTED_TOTAL_NODES = 77
EXPECTED_PAGE_COUNT = 42
EXPECTED_FOLDER_COUNT = 35
EXPECTED_MAX_DEPTH = 12

# Title format: "{type}{number}-L{level}"
TITLE_PATTERN = re.compile(r"^([pf])(\d+)-L(\d+)$")
TYPE_MAP = {"p": "page", "f": "folder"}


def parse_title(title: str) -> tuple[str, int, int] | None:
    """Parse title to extract (type_prefix, number, level)."""
    match = TITLE_PATTERN.match(title)
    if not match:
        return None
    return match.group(1), int(match.group(2)), int(match.group(3))


def test():
    """
    Comprehensive test for crawl_descendants_with_cache.

    Single fetch, all validations in one loop.
    """
    print("\n" + "=" * 70)
    print("Comprehensive Crawler Test")
    print("=" * 70)

    # === Fetch once ===
    entities = crawl_descendants_with_cache(
        client=client,
        root_id=homepage_id,
        root_type=DescendantTypeEnum.page,
        cache=one.cache,
    )
    print(f"\nFetched {len(entities)} entities")

    # === Check 1: Total count ===
    assert len(entities) == EXPECTED_TOTAL_NODES, (
        f"Expected {EXPECTED_TOTAL_NODES} entities, got {len(entities)}"
    )
    print(f"[PASS] Total count: {len(entities)}")

    # === Check 2: Sorted by position_path ===
    position_paths = [e.position_path for e in entities]
    assert position_paths == sorted(position_paths), "Entities not sorted by position_path"
    print("[PASS] Entities sorted by position_path")

    # === Single loop for all per-entity checks ===
    pages_count = 0
    folders_count = 0
    max_level = 0
    l12_entities = []
    l5_entities = []

    for entity in entities:
        title = entity.node.title
        parsed = parse_title(title)

        if parsed is None:
            print(f"  WARNING: Cannot parse title: {title}")
            continue

        type_prefix, number, level = parsed

        # Check 3: Type prefix matches node type
        expected_type = TYPE_MAP[type_prefix]
        actual_type = entity.node.type
        assert actual_type == expected_type, (
            f"Type mismatch for {title}: expected '{expected_type}', got '{actual_type}'"
        )

        # Check 4: Level matches lineage length
        actual_level = len(entity.lineage)
        assert actual_level == level, (
            f"Level mismatch for {title}: expected {level}, got {actual_level}"
        )

        # Check 5: Lineage structure - first element is self
        assert entity.lineage[0].id == entity.node.id, (
            f"First lineage element should be self for {title}"
        )

        # Check 6: Path lengths match
        assert len(entity.id_path) == len(entity.title_path) == len(entity.position_path), (
            f"Path lengths mismatch for {title}"
        )

        # Check 7: Paths are root-to-leaf order (last element is self)
        assert entity.id_path[-1] == entity.node.id, (
            f"id_path should end with self for {title}"
        )
        assert entity.title_path[-1] == entity.node.title, (
            f"title_path should end with self for {title}"
        )

        # Track stats
        if type_prefix == "p":
            pages_count += 1
        elif type_prefix == "f":
            folders_count += 1
        else:
            pass
        max_level = max(max_level, level)

        # Collect samples for reporting
        if level == 12:
            l12_entities.append(entity)
        if level == 5:
            l5_entities.append(entity)

    # === Check 8: Pages count ===
    assert pages_count == EXPECTED_PAGE_COUNT, (
        f"Expected {EXPECTED_PAGE_COUNT} pages, got {pages_count}"
    )
    print(f"[PASS] Pages count: {pages_count}")

    # === Check 9: Folders count ===
    assert folders_count == EXPECTED_FOLDER_COUNT, (
        f"Expected {EXPECTED_FOLDER_COUNT} folders, got {folders_count}"
    )
    print(f"[PASS] Folders count: {folders_count}")

    # === Check 10: Max depth ===
    assert max_level == EXPECTED_MAX_DEPTH, (
        f"Expected max depth {EXPECTED_MAX_DEPTH}, got {max_level}"
    )
    print(f"[PASS] Max depth: {max_level}")

    # === Check 11: L12 entities exist (deep hierarchy test) ===
    assert len(l12_entities) > 0, "No L12 entities found"
    print(f"[PASS] L12 entities found: {len(l12_entities)}")

    # Print checks summary
    print("\n[PASS] All per-entity checks:")
    print("  - Type prefix matches node type")
    print("  - Level matches lineage length")
    print("  - Lineage first element is self")
    print("  - Path lengths consistent")
    print("  - Paths are root-to-leaf order")

    # === Sample output for debugging ===
    print("\n--- Sample L12 entity ---")
    if l12_entities:
        e = l12_entities[0]
        print(f"  Title: {e.node.title}")
        print(f"  Lineage length: {len(e.lineage)}")
        print(f"  Title path: {e.title_path}")

    print("\n--- Sample L5 entity ---")
    if l5_entities:
        e = l5_entities[0]
        print(f"  Title: {e.node.title}")
        print(f"  id_path: {e.id_path}")
        print(f"  title_path: {e.title_path}")
        print(f"  position_path: {e.position_path}")
        print(f"  id_breadcrumb_path: {e.id_breadcrumb_path}")
        print(f"  title_breadcrumb_path: {e.title_breadcrumb_path}")

    print("\n--- First 10 entities (depth-first order) ---")
    for i, entity in enumerate(entities[:10]):
        print(f"  {i+1}. {entity.node.title} - pos: {entity.position_path}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    from docpack_confluence.tests import run_unit_test

    run_unit_test(__file__)
