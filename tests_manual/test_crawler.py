# -*- coding: utf-8 -*-

"""
Manual tests for crawl_descendants and crawl_descendants_with_cache.

These tests require real Confluence API access. Run manually, not in CI.

Test Hierarchy (77 nodes, 12 levels):
- Branch 1: p01-L1 -> deep path with clustering at f04-L4 and f08-L8
- Branch 2: p01-L1/f55-L2 -> single chain to L12
- Branch 3: f66-L1 -> single chain to L12 (folder as root)

Expected crawler behavior:
- 3 iterations to fetch all 77 nodes (depth=5 limit)
- Iteration 1: homepage -> L1-L5
- Iteration 2: L4 parents -> L5-L9
- Iteration 3: L8 parents -> L9-L12
"""

from docpack_confluence.crawler import (
    crawl_descendants,
    crawl_descendants_with_cache,
)
from docpack_confluence.constants import DescendantTypeEnum
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import homepage_id
from docpack_confluence.one import one


# Test space configuration
site_url = client.url

# Expected counts based on hierarchy_specs
EXPECTED_TOTAL_NODES = 77  # Total nodes in hierarchy
EXPECTED_PAGE_COUNT = 42  # Pages only (prefix 'p')
EXPECTED_FOLDER_COUNT = 35  # Folders only (prefix 'f')
EXPECTED_MAX_DEPTH = 12  # Deepest level


class TestCrawlDescendants:
    """Tests for crawl_descendants function."""

    def test_fetch_all_nodes(self):
        """
        Test that crawler fetches all 77 nodes in the 12-level hierarchy.

        This validates the Parent Clustering Algorithm works correctly
        with depth > 5.
        """
        print("\n" + "=" * 60)
        print("Test: Fetch all nodes")
        print("=" * 60)

        entities = crawl_descendants(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            verbose=True,
        )

        print(f"\nFetched {len(entities)} entities")
        print(f"Expected: {EXPECTED_TOTAL_NODES} nodes")

        # Validate count
        assert (
            len(entities) == EXPECTED_TOTAL_NODES
        ), f"Expected {EXPECTED_TOTAL_NODES} entities, got {len(entities)}"

        # Count pages vs folders
        pages = [e for e in entities if e.node.type == "page"]
        folders = [e for e in entities if e.node.type == "folder"]
        print(f"Pages: {len(pages)}, Folders: {len(folders)}")

        assert (
            len(pages) == EXPECTED_PAGE_COUNT
        ), f"Expected {EXPECTED_PAGE_COUNT} pages, got {len(pages)}"
        assert (
            len(folders) == EXPECTED_FOLDER_COUNT
        ), f"Expected {EXPECTED_FOLDER_COUNT} folders, got {len(folders)}"

        print("PASSED: All nodes fetched correctly")

    def test_entities_sorted_by_position_path(self):
        """
        Test that entities are sorted by position_path (depth-first order).
        """
        print("\n" + "=" * 60)
        print("Test: Entities sorted by position_path")
        print("=" * 60)

        entities = crawl_descendants(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            verbose=False,
        )

        # Verify sorting
        position_paths = [e.position_path for e in entities]
        sorted_paths = sorted(position_paths)

        assert position_paths == sorted_paths, "Entities not sorted by position_path"

        # Print first 10 entities to visualize order
        print("\nFirst 10 entities (depth-first order):")
        for i, entity in enumerate(entities[:10]):
            print(f"  {i+1}. {entity.node.title} - pos: {entity.position_path}")

        print("PASSED: Entities correctly sorted")

    def test_entity_lineage_structure(self):
        """
        Test that Entity lineage is correctly built.

        Lineage should be [self, parent, grandparent, ..., root_ancestor]
        """
        print("\n" + "=" * 60)
        print("Test: Entity lineage structure")
        print("=" * 60)

        entities = crawl_descendants(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            verbose=False,
        )

        # Find a deep entity (L12)
        deep_entities = [e for e in entities if "-L12" in e.node.title]
        assert len(deep_entities) > 0, "No L12 entities found"

        deep_entity = deep_entities[0]
        print(f"\nDeep entity: {deep_entity.node.title}")
        print(f"Lineage length: {len(deep_entity.lineage)}")
        print(f"Title path: {deep_entity.title_path}")

        # Lineage should have 12 nodes (L1 to L12)
        assert (
            len(deep_entity.lineage) == 12
        ), f"Expected lineage length 12, got {len(deep_entity.lineage)}"

        # First in lineage should be the entity itself
        assert (
            deep_entity.lineage[0].id == deep_entity.node.id
        ), "First lineage element should be self"

        # id_path should be root-to-leaf order
        id_path = deep_entity.id_path
        assert id_path[-1] == deep_entity.node.id, "Last id_path element should be self"

        print("PASSED: Lineage structure correct")

    def test_entity_properties(self):
        """
        Test Entity computed properties: id_path, title_path, position_path.
        """
        print("\n" + "=" * 60)
        print("Test: Entity properties")
        print("=" * 60)

        entities = crawl_descendants(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            verbose=False,
        )

        # Pick a mid-level entity
        mid_entities = [e for e in entities if "-L5" in e.node.title]
        assert len(mid_entities) > 0, "No L5 entities found"

        entity = mid_entities[0]
        print(f"\nEntity: {entity.node.title}")
        print(f"  id_path: {entity.id_path}")
        print(f"  title_path: {entity.title_path}")
        print(f"  position_path: {entity.position_path}")
        print(f"  id_breadcrumb_path: {entity.id_breadcrumb_path}")
        print(f"  title_breadcrumb_path: {entity.title_breadcrumb_path}")

        # Validate path lengths match
        assert (
            len(entity.id_path) == len(entity.title_path) == len(entity.position_path)
        ), "Path lengths should match"

        # Validate paths are root-to-leaf order
        assert entity.id_path[-1] == entity.node.id
        assert entity.title_path[-1] == entity.node.title

        print("PASSED: Entity properties correct")


class TestCrawlDescendantsWithCache:
    """Tests for crawl_descendants_with_cache function."""

    def test_cache_miss_fetches_data(self):
        """
        Test that cache miss triggers API fetch.
        """
        print("\n" + "=" * 60)
        print("Test: Cache miss fetches data")
        print("=" * 60)

        # Use unique cache key to ensure cache miss
        cache_key = "test_cache_miss_fetches_data"
        one.cache.delete(cache_key)

        entities = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=one.cache,
            cache_key=cache_key,
            expire=60,
            verbose=True,
        )

        print(f"\nFetched {len(entities)} entities")
        assert len(entities) == EXPECTED_TOTAL_NODES

        # Verify data was cached
        cached_data = one.cache.get(cache_key)
        assert cached_data is not None, "Data should be cached"

        # Cleanup
        one.cache.delete(cache_key)
        print("PASSED: Cache miss correctly fetches and caches data")

    def test_cache_hit_returns_cached_data(self):
        """
        Test that cache hit returns cached data without API call.
        """
        print("\n" + "=" * 60)
        print("Test: Cache hit returns cached data")
        print("=" * 60)

        cache_key = "test_cache_hit_returns_cached_data"
        one.cache.delete(cache_key)

        # First call - cache miss
        entities1 = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=one.cache,
            cache_key=cache_key,
            expire=60,
            verbose=False,
        )
        print(f"First call: {len(entities1)} entities")

        # Second call - cache hit (should be fast, no API call)
        print("Second call (should be instant from cache)...")
        entities2 = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=one.cache,
            cache_key=cache_key,
            expire=60,
            verbose=False,
        )
        print(f"Second call: {len(entities2)} entities")

        # Validate same data
        assert len(entities1) == len(entities2)

        # Cleanup
        one.cache.delete(cache_key)
        print("PASSED: Cache hit returns correct data")

    def test_force_refresh_bypasses_cache(self):
        """
        Test that force_refresh=True bypasses cache and fetches fresh data.
        """
        print("\n" + "=" * 60)
        print("Test: Force refresh bypasses cache")
        print("=" * 60)

        cache_key = "test_force_refresh_bypasses_cache"
        one.cache.delete(cache_key)

        # First call - populate cache
        entities1 = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=one.cache,
            cache_key=cache_key,
            expire=60,
            verbose=False,
        )
        print(f"First call: {len(entities1)} entities")

        # Second call with force_refresh - should fetch again
        print("Force refresh call...")
        entities2 = crawl_descendants_with_cache(
            client=client,
            root_id=homepage_id,
            root_type=DescendantTypeEnum.page,
            cache=one.cache,
            cache_key=cache_key,
            expire=60,
            force_refresh=True,
            verbose=True,
        )
        print(f"Force refresh call: {len(entities2)} entities")

        assert len(entities2) == EXPECTED_TOTAL_NODES

        # Cleanup
        one.cache.delete(cache_key)
        print("PASSED: Force refresh works correctly")


if __name__ == "__main__":
    from docpack_confluence.tests import run_unit_test

    run_unit_test(__file__)
