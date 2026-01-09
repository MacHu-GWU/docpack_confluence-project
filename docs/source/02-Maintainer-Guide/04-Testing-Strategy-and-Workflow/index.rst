.. _testing-strategy-and-workflow:

Testing Strategy and Workflow
==============================================================================

This document describes the testing strategy and workflow for developing and
validating the Confluence data fetching functionality. It covers the test data
design, key functions, and the end-to-end testing workflow.


Overview
------------------------------------------------------------------------------

Testing the Confluence crawler and filtering system requires real API calls to
Confluence. We designed a comprehensive testing workflow with these components:

1. **Test Data Structure**: A carefully designed hierarchy in ``tests/data.py``
2. **CRUD Functions**: Create, read, and delete test data in real Confluence
3. **Crawler Validation**: Verify the Parent Clustering Algorithm works correctly
4. **Filter Testing**: Test include/exclude pattern matching

The key insight is that we can **programmatically create and destroy test data**,
making our tests reproducible and isolated.


Test Data Design
------------------------------------------------------------------------------

Location: :mod:`docpack_confluence.tests.data`

We designed a 12-level deep hierarchy with 77 nodes to thoroughly test the
Parent Clustering Algorithm, which must handle the Confluence API's depth=5
limitation.

**Title Naming Convention**

Each node's title encodes important metadata::

    {type}{sequence:02d}-L{level}

Where:

- ``type``: ``p`` for page, ``f`` for folder
- ``sequence``: Two-digit sequential number (01-77)
- ``level``: Depth level (L1-L12)

Examples:

- ``p01-L1``: Page #1 at level 1
- ``f04-L4``: Folder #4 at level 4
- ``p77-L12``: Page #77 at level 12

**Hierarchy Structure**

The hierarchy has three branches to test different scenarios::

    Branch 1: p01-L1 -> deep path with clustering at L4-L5 and L8-L9
    Branch 2: p01-L1/f55-L2 -> single chain to L12
    Branch 3: f66-L1 -> single chain to L12 (folder as root)

Key characteristics:

- **77 total nodes** (42 pages, 35 folders)
- **12 levels deep** (requires 3 crawler iterations with depth=5)
- **Clustering parents** at L4 and L8 (nodes with 4-6 children each)
- **Mixed page/folder structure** to test both entity types

**Hierarchy Spec Format**

The hierarchy is defined as a list of path strings::

    hierarchy_specs = [
        "p01-L1",                                    # Root page
        "p01-L1/p02-L2",                             # Child of p01
        "p01-L1/p02-L2/p03-L3",                      # Grandchild
        "p01-L1/p02-L2/p03-L3/f04-L4",              # Clustering parent (folder)
        "p01-L1/p02-L2/p03-L3/f04-L4/p05-L5",       # Child under f04
        # ... 72 more entries
    ]

This format is:

- **Human readable**: Easy to visualize the hierarchy
- **Order dependent**: Parent must be defined before children
- **Self-documenting**: Path shows exact location in tree


Key Functions in shortcuts.py
------------------------------------------------------------------------------

Location: :mod:`docpack_confluence.shortcuts`

**get_descendants_of_page**

Fetches all descendants of a page using pagination::

    def get_descendants_of_page(
        client: Confluence,
        page_id: int,
        limit: int = 9999,
        depth: int = 5,  # API maximum
    ) -> Iterator[GetPageDescendantsResponseResult]:
        """
        Crawls and retrieves all descendant pages of a given Confluence page.
        """

**get_descendants_of_folder**

Fetches all descendants of a folder (added later to reduce API calls)::

    def get_descendants_of_folder(
        client: Confluence,
        folder_id: int,
        limit: int = 9999,
        depth: int = 5,
    ) -> Iterator[GetFolderDescendantsResponseResult]:
        """
        Crawls and retrieves all descendant entities of a given Confluence folder.
        """

These two functions are the foundation for the Parent Clustering Algorithm.


Parent Clustering Algorithm (crawler.py)
------------------------------------------------------------------------------

Location: :mod:`docpack_confluence.crawler`

The :func:`~docpack_confluence.crawler.crawl_descendants` function is the
core algorithm that fetches **complete hierarchies** regardless of depth.

**Why This Algorithm?**

The Confluence API limits ``get_descendants`` to depth=5. For a 12-level hierarchy:

- **Naive approach**: Call API for each boundary node (100+ calls, most return empty)
- **Parent Clustering**: Cluster boundary nodes by parent, call from parent level (~3-10 calls)

**Algorithm Overview**

.. code-block:: text

    ITERATION 1:
    ├── Fetch from homepage (depth=5) → L1-L5 nodes
    ├── Identify boundary nodes (at depth=5)
    ├── Cluster by parents → unique L4 parents
    └── Next iteration fetches from L4 parents

    ITERATION 2:
    ├── Fetch from each L4 parent (depth=5) → L5-L9 nodes
    ├── Deduplicate (skip already-fetched nodes)
    ├── Identify new boundary nodes (at depth=5 relative to parent)
    ├── Cluster by parents → unique L8 parents
    └── Next iteration fetches from L8 parents

    ITERATION 3:
    ├── Fetch from each L8 parent (depth=5) → L9-L12 nodes
    └── No boundary nodes → DONE

**Key Implementation Details**

1. **MIN_DEPTH = 2**: Algorithm requires depth >= 2 to find parents in entity_pool
2. **Entity dataclass**: Stores node + lineage (path to root)
3. **Deduplication**: Nodes are only processed once using entity_pool dict
4. **Sorted output**: Results sorted by position_path for depth-first order


CRUD Functions for Test Data
------------------------------------------------------------------------------

**delete_pages_and_folders_in_space**

Deletes all pages and folders in a space::

    def delete_pages_and_folders_in_space(
        client: Confluence,
        space_id: int,
        purge: bool = False,  # Keep in trash, don't permanently delete
        verbose: bool = True,
    ) -> None:

**Important**: The function deletes from **deepest level first** to avoid
"parent can't be deleted" errors::

    Delete order for max_depth=3:
    1. Delete all L3 entities
    2. Delete all L2 entities
    3. Delete all L1 entities

**Note**: ``purge=False`` is recommended. Setting ``purge=True`` only works for
items already in the trash (Confluence API limitation).

**create_pages_and_folders**

Creates pages and folders based on hierarchy specs::

    def create_pages_and_folders(
        client: Confluence,
        space_id: int,
        hierarchy_specs: list[str],
        max_retries: int = 3,
        initial_delay: float = 1.0,
        retry_on: set[int] | None = None,  # Default: {404}
    ) -> dict[str, str]:  # title -> created ID

**Features**:

- **Auto-retry**: Handles 404 errors when parent isn't ready yet
- **Exponential backoff**: 1s, 2s, 4s delay between retries
- **Order-dependent**: Creates parents before children
- **Returns ID map**: Useful for subsequent operations

**execute_with_retry**

Generic retry wrapper used by create_pages_and_folders::

    def execute_with_retry(
        request: T_REQUEST,
        client: Confluence,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        retry_on: set[int] | None = None,  # Default: {404}
        verbose: bool = True,
    ) -> T_RESPONSE_TYPE:


Testing Workflow
------------------------------------------------------------------------------

Location: ``tests_manual/test.py``

**Step 1: Clean Up Existing Data**

.. code-block:: python

    def delete_all_pages_and_folders():
        """Delete all pages and folders in the test space."""
        delete_pages_and_folders_in_space(
            client=client,
            space_id=space_id,
            purge=False,
        )

**Step 2: Create Test Hierarchy**

.. code-block:: python

    def create_deep_hierarchy_pages_and_folders():
        """Create a 12-level deep hierarchy with 77 nodes."""
        create_pages_and_folders(
            client=client,
            space_id=space_id,
            hierarchy_specs=hierarchy_specs,
        )

**Step 3: Validate Crawler**

.. code-block:: python

    def test_crawl_descendants():
        """Test the Parent Clustering Algorithm crawler."""
        entities = crawl_descendants(
            client=client,
            homepage_id=homepage_id,
            verbose=True,
        )
        # Print all entity IDs for creating test patterns
        for entity in entities:
            node = entity.node
            print(f"{node.title}: {node.id} ({node.type})")

This is the **most critical test** - it validates that:

1. All 77 nodes are fetched (despite depth > 5)
2. Algorithm completes in 3 iterations (not 100+)
3. Entities are sorted in depth-first order
4. Lineage information is correct

**Step 4: Test Filtering**

.. code-block:: python

    def test_select_pages():
        """Test include/exclude pattern filtering."""
        # Test 1: No filter (all 42 pages)
        pages = select_pages(client=client, space_id=space_id)

        # Test 2: Include only Branch 3
        pages = select_pages(
            client=client,
            space_id=space_id,
            include=[f"{site_url}/wiki/spaces/DPPROJ1/folder/655426125/**"],
        )

        # Test 3: Include with exclude
        pages = select_pages(
            client=client,
            space_id=space_id,
            include=[f"{site_url}/wiki/spaces/DPPROJ1/pages/655425960/**"],
            exclude=[f"{site_url}/wiki/spaces/DPPROJ1/folder/655491640/**"],
        )


Test Cases Summary
------------------------------------------------------------------------------

Our test suite covers 5 key scenarios:

.. list-table::
   :header-rows: 1
   :widths: 10 40 25 25

   * - Test
     - Description
     - Pattern
     - Expected Result
   * - 1
     - No filter (all pages)
     - None
     - 42 pages
   * - 2
     - Include Branch 3 only
     - f66-L1/**
     - 6 pages
   * - 3
     - Include Branch 1+2, exclude deep subtree
     - p01-L1/** - f08-L8/**
     - 31 pages
   * - 4
     - Include two separate subtrees
     - p03-L3/** + f66-L1/**
     - 25 pages
   * - 5
     - Descendants only (not self)
     - f04-L4/*
     - 11 pages


Development Philosophy
------------------------------------------------------------------------------

**The Hard Part is Done**

Once :func:`~docpack_confluence.crawler.crawl_descendants` is working:

1. We have **complete hierarchy data** regardless of depth
2. We have **lineage information** for each entity
3. **Filtering becomes trivial**: Just iterate and match patterns

The Parent Clustering Algorithm is the core innovation. Everything else
(include/exclude patterns, caching, export) builds on this foundation.

**Why Two-Phase API Design?**

We provide two functions for different use cases:

.. code-block:: python

    # Pure filtering (for cached entities)
    def filter_pages(entities, include, exclude) -> list[Entity]:
        """Filter entities without I/O."""

    # Convenience wrapper (fetches + filters)
    def select_pages(client, space_id, include, exclude) -> list[Entity]:
        """Fetch from API and filter."""

This allows:

- **Caching**: Fetch once, filter multiple times
- **Testing**: Test filtering logic without API calls
- **Flexibility**: Users choose their caching strategy


Quick Reference
------------------------------------------------------------------------------

**Create Test Data**::

    from docpack_confluence.tests.data import hierarchy_specs
    from docpack_confluence.shortcuts import create_pages_and_folders

    create_pages_and_folders(client, space_id, hierarchy_specs)

**Delete Test Data**::

    from docpack_confluence.shortcuts import delete_pages_and_folders_in_space

    delete_pages_and_folders_in_space(client, space_id, purge=False)

**Crawl Hierarchy**::

    from docpack_confluence.crawler import crawl_descendants

    entities = crawl_descendants(client, homepage_id, verbose=True)
    # Returns 77 entities in 3 iterations

**Filter Pages**::

    from docpack_confluence.shortcuts import filter_pages, select_pages

    # With pre-fetched entities
    pages = filter_pages(entities, include=[".../**"], exclude=[".../*"])

    # Fetch and filter in one call
    pages = select_pages(client, space_id, include=[".../**"])


Manual Testing
------------------------------------------------------------------------------

The ``tests_manual/`` directory contains manual tests that require real
Confluence API access. **These are NOT unit tests** - they are run manually
during development and not included in CI.

**test_crawler.py**

Location: ``tests_manual/test_crawler.py``

Comprehensive tests for the crawler functionality:

- Validates all 77 nodes are fetched
- Verifies page/folder counts (42 pages, 35 folders)
- Checks 12-level depth handling
- Tests entity lineage structure
- Validates cache functionality

Run manually::

    .venv/bin/python tests_manual/test_crawler.py

**test.py**

Location: ``tests_manual/test.py``

Interactive test file with helper functions:

- ``create_deep_hierarchy_pages_and_folders()``: Create test data
- ``delete_all_pages_and_folders()``: Clean up test data
- ``test_crawl_descendants()``: Test crawler and print entity IDs
- ``test_select_pages()``: Test include/exclude filtering

.. note::

    Always ensure test data exists before running crawler tests. Use
    ``create_deep_hierarchy_pages_and_folders()`` if the test space is empty.
