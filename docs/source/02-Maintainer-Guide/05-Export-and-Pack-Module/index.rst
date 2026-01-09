.. _export-and-pack-module:

Export and Pack Module
==============================================================================

This document explains the export and pack modules that form the public API
for exporting Confluence pages to XML files for AI knowledge base ingestion.


Module Overview
------------------------------------------------------------------------------

The export functionality is built in two layers:

1. **exporter.py** - Low-level export utilities
2. **pack.py** - High-level public API


exporter.py - Export Utilities
------------------------------------------------------------------------------

Location: :mod:`docpack_confluence.exporter`

This module provides low-level functions for exporting pages to files:

**export_pages_to_xml_files()**

Exports a list of :class:`~docpack_confluence.page.Page` objects to individual
XML files. Each file is named using the page's breadcrumb path (ID or title based).

.. code-block:: python

    from docpack_confluence.exporter import export_pages_to_xml_files

    export_pages_to_xml_files(
        pages=pages,           # List of Page objects
        dir_out=Path("./out"), # Output directory
        breadcrumb_type=BreadCrumbTypeEnum.title,  # Filename format
        clean_output_dir=True, # Remove dir before export
    )

**merge_files()**

Merges all exported XML files into a single "all-in-one" document for AI
context ingestion:

.. code-block:: python

    from docpack_confluence.exporter import merge_files

    merge_files(
        dir_in_list=[Path("./space1"), Path("./space2")],
        path_out=Path("./all_in_one.xml"),
        ext=".xml",
    )


pack.py - Public API
------------------------------------------------------------------------------

Location: :mod:`docpack_confluence.pack`

This module provides the high-level API for end-to-end export operations.

**SpaceExportConfig**

Configuration for exporting pages from a single Confluence space:

.. code-block:: python

    from docpack_confluence.pack import SpaceExportConfig

    config = SpaceExportConfig(
        client=confluence_client,
        space_id=12345,              # or space_key="DEMO"
        include=[                    # URL patterns to include
            "https://example.atlassian.net/wiki/.../pages/111/**",
        ],
        exclude=[                    # URL patterns to exclude
            "https://example.atlassian.net/wiki/.../pages/222/*",
        ],
        breadcrumb_type=BreadCrumbTypeEnum.title,
        ignore_to_markdown_error=True,
    )

**ExportSpec**

Specification for exporting from multiple spaces at once:

.. code-block:: python

    from docpack_confluence.pack import ExportSpec, SpaceExportConfig

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(client=client, space_id=111, include=[...]),
            SpaceExportConfig(client=client, space_id=222, include=[...]),
        ],
        dir_out=Path("./output"),
    )

    # Execute the export
    spec.export()

    # Output structure:
    # ./output/
    #   space_id_111/
    #     Page A ~ Page B.xml
    #     Page A ~ Page C.xml
    #   space_id_222/
    #     Page X ~ Page Y.xml
    #   all_in_one_knowledge_base.txt   # Merged file


Export Workflow
------------------------------------------------------------------------------

The export workflow consists of these steps:

1. **Crawl**: Fetch page hierarchy using :func:`~docpack_confluence.crawler.crawl_descendants`
2. **Filter**: Apply include/exclude patterns using :func:`~docpack_confluence.shortcuts.filter_pages`
3. **Fetch Content**: Get full page content using :func:`~docpack_confluence.shortcuts.get_pages_by_ids`
4. **Build Pages**: Create :class:`~docpack_confluence.page.Page` objects with entity + content
5. **Export XML**: Write individual XML files with metadata and markdown content
6. **Merge**: Combine all XML files into a single knowledge base file


Output Format
------------------------------------------------------------------------------

Each exported XML file contains:

.. code-block:: xml

    <confluence_page>
        <source_type>confluence</source_type>
        <confluence_url>https://example.atlassian.net/wiki/...</confluence_url>
        <title>Page Title</title>
        <markdown_content>
            # Page Title

            Converted markdown content...
        </markdown_content>
    </confluence_page>

The ``all_in_one_knowledge_base.txt`` file concatenates all XML files for
easy ingestion into AI platforms.


Manual Testing with test_pack.py
------------------------------------------------------------------------------

Location: ``tests_manual/test_pack.py``

This file provides a manual test for the export functionality using a real
Confluence instance. **This is NOT a unit test** - it requires actual API
access and is run manually during development.

**Running the Test**

.. code-block:: bash

    # Run manually (not via pytest)
    .venv/bin/python tests_manual/test_pack.py

**Test Structure**

.. code-block:: python

    from docpack_confluence.pack import SpaceExportConfig, ExportSpec
    from docpack_confluence.tests.client import client
    from docpack_confluence.tests.data import space_id

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_id=space_id,
                include=[".../**"],  # Include patterns
                exclude=[".../*"],   # Exclude patterns
            ),
        ],
        dir_out=Path("./tmp"),
    )
    spec.export()

**What to Verify**

After running the test, check:

1. Output directory structure is correct
2. Individual XML files have proper naming (breadcrumb path)
3. XML content includes all expected fields
4. ``all_in_one_knowledge_base.txt`` contains merged content
5. Include/exclude patterns worked correctly


Development Workflow
------------------------------------------------------------------------------

When developing or debugging the export functionality:

1. **Setup Test Data**: Use ``tests_manual/test.py`` to create test hierarchy
2. **Run Export**: Execute ``tests_manual/test_pack.py``
3. **Inspect Output**: Check ``tests_manual/tmp/`` directory
4. **Iterate**: Modify code and re-run as needed

.. note::

    The test uses the same 77-node test hierarchy (12 levels) used for
    crawler testing. See :ref:`testing-strategy-and-workflow` for details
    on the test data structure.
