.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.1 (2025-01-09)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Initial release of ``docpack_confluence`` - a library for batch exporting Confluence pages to AI-ready formats.

**Core Components**

- **Page Model** (:class:`~docpack_confluence.page.Page`): Data model representing Confluence pages with lineage tracking, sort keys, and hierarchy properties.
- **Entity Model** (:class:`~docpack_confluence.crawler.Entity`): Lightweight entity representation for efficient page/folder traversal in Confluence space hierarchies.
- **Space Crawler** (:func:`~docpack_confluence.crawler.crawl_descendants`): Crawls Confluence space hierarchies with parent clustering algorithm to handle API depth limitations.
- **Selector System** (:class:`~docpack_confluence.selector.Selector`): Gitignore-style pattern matching for precise page selection using ``include``/``exclude`` patterns.
- **Export Pipeline** (:func:`~docpack_confluence.exporter.export_pages_to_xml_files`): Exports pages to XML-wrapped Markdown files with metadata and source URLs.
- **All-in-One Export** (:func:`~docpack_confluence.exporter.merge_files`): Merges exported files into a single knowledge base file for AI platforms.

**High-Level API**

- :class:`~docpack_confluence.pack.SpaceExportConfig`: Configuration class for single space exports with include/exclude patterns.
- :class:`~docpack_confluence.pack.ExportSpec`: Orchestrates multi-space exports with unified output directory.

**Caching Support**

- Built-in caching via ``diskcache`` for efficient repeated exports.
- Cache-enabled variants: :func:`~docpack_confluence.shortcuts.get_pages_in_space_with_cache`, :func:`~docpack_confluence.shortcuts.get_descendants_of_page_with_cache`, :func:`~docpack_confluence.crawler.crawl_descendants_with_cache`.
- Serialization utilities: :func:`~docpack_confluence.shortcuts.serialize_many`, :func:`~docpack_confluence.shortcuts.deserialize_many` for page data persistence.

**Utility Functions**

- :func:`~docpack_confluence.shortcuts.get_space_by_id`, :func:`~docpack_confluence.shortcuts.get_space_by_key`: Space retrieval helpers.
- :func:`~docpack_confluence.shortcuts.get_pages_by_ids`, :func:`~docpack_confluence.shortcuts.get_pages_in_space`: Page fetching utilities.
- :func:`~docpack_confluence.shortcuts.get_descendants_of_page`, :func:`~docpack_confluence.shortcuts.get_descendants_of_folder`: Hierarchy traversal.
- :func:`~docpack_confluence.shortcuts.create_pages_and_folders`: Create page/folder structures with retry logic.
- :func:`~docpack_confluence.shortcuts.delete_pages_and_folders_in_space`: Clean up test data in correct dependency order.
- :func:`~docpack_confluence.utils.safe_write`: Safe file writing utility.

**Pattern Matching**

- Support for gitignore-style patterns with match modes:
    - ``/**`` - Include page and all descendants
    - ``/*`` - Include descendants only (not the page itself)
    - No suffix - Include only the specific page
- :func:`~docpack_confluence.selector.parse_pattern`: Parse pattern strings into match rules.
- :func:`~docpack_confluence.selector.is_match`: Check if an entity matches a pattern.
- :class:`~docpack_confluence.selector.MatchMode`: Enum defining match modes (EXACT, CHILDREN, DESCENDANTS).
