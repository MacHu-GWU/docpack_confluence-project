.. _quick-start:

Quick Start
==============================================================================

``docpack_confluence`` is a Python library for batch exporting Confluence pages to Markdown format, designed specifically for AI knowledge base integration. It converts your Confluence documentation into AI-friendly formats that can be easily uploaded to AI assistants like Claude Projects, ChatGPT Knowledge, or RAG pipelines.


Why Use docpack_confluence?
------------------------------------------------------------------------------

- **AI-Ready Export**: Converts Confluence pages to Markdown, focusing on content preservation rather than pixel-perfect formatting
- **Rich Text Support**: Preserves headings, lists, tables, code blocks, and other rich text formatting where possible
- **Flexible Selection**: Powerful include/exclude patterns to export exactly the pages you need
- **Multi-Space Support**: Export from multiple Confluence sites and spaces in a single operation
- **Dual Output Format**: Generate individual files per page AND an all-in-one merged file for easy drag-and-drop to AI platforms


Installation
------------------------------------------------------------------------------

.. code-block:: bash

    pip install docpack-confluence


Basic Usage
------------------------------------------------------------------------------

Here's a minimal example to export all pages from a Confluence space:

.. code-block:: python

    from pathlib import Path
    from sanhe_confluence_sdk.api import Confluence
    from docpack_confluence.api import SpaceExportConfig, ExportSpec

    # 1. Create Confluence client
    client = Confluence(
        url="https://your-domain.atlassian.net",
        username="your-email@example.com",  # Your Atlassian account email
        password="your-api-token",  # API token from https://id.atlassian.com/manage-profile/security/api-tokens
    )

    # 2. Configure export specification
    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="MYSPACE",  # Or use space_id=12345
            ),
        ],
        dir_out=Path("./confluence_export"),  # Output directory
    )

    # 3. Execute export
    spec.export()

.. warning::

    **Important**: The ``dir_out`` directory will be completely deleted and recreated during export to ensure a clean output. Always specify a dedicated directory that doesn't contain other important files.


Output Structure
------------------------------------------------------------------------------

After running the export, you'll find the following structure in your output directory:

.. code-block:: text

    confluence_export/
    ├── space_key_MYSPACE/
    │   ├── Homepage ~ Page Title A.xml
    │   ├── Homepage ~ Page Title A ~ Child Page.xml
    │   ├── Homepage ~ Page Title B.xml
    │   └── ...
    └── all_in_one_knowledge_base.txt

**Individual XML Files**

Each Confluence page is exported as a separate XML file in a subdirectory named after the space (``space_key_MYSPACE`` or ``space_id_12345``). The filename uses the page's breadcrumb path (hierarchy) with ``~`` as separator, making it easy to understand the page's location in the Confluence tree.

Each XML file contains:

.. code-block:: xml

    <document>
        <source_type>Confluence Page</source_type>
        <confluence_url>https://your-domain.atlassian.net/wiki/spaces/MYSPACE/pages/123456/Page+Title</confluence_url>
        <title>Page Title</title>
        <markdown_content>
    # Page Title

    Your page content in Markdown format...
        </markdown_content>
    </document>

**All-in-One File**

The ``all_in_one_knowledge_base.txt`` file concatenates all exported pages into a single document. This is especially useful when you want to:

- **Drag and drop** directly into AI chat interfaces for instant context
- **Upload to AI knowledge bases**: ChatGPT Project Knowledge Base, Claude Project Files, Gemini Gems, etc.
- **Ingest into vector stores**: Feed the exported files into your own RAG pipeline or vector database
- **Share easily**: Distribute the entire knowledge base as a single file


Selective Export with Include/Exclude Patterns
------------------------------------------------------------------------------

The real power of ``docpack_confluence`` lies in its filtering system. You can precisely control which pages to export using URL patterns with wildcard suffixes.

Pattern Syntax
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Patterns use Confluence page or folder URLs with optional wildcards:

.. list-table::
   :header-rows: 1
   :widths: 15 35 50

   * - Suffix
     - Mode
     - Description
   * - (none)
     - SELF
     - Export only the specified page/folder itself
   * - ``/*``
     - DESCENDANTS
     - Export all children and descendants, but NOT the node itself
   * - ``/**``
     - RECURSIVE
     - Export the node itself AND all its descendants

**Getting URLs from Confluence**

To get a page URL, simply copy it from your browser's address bar when viewing the page:

- **Page URL**: ``https://your-domain.atlassian.net/wiki/spaces/MYSPACE/pages/123456/Page-Title``
- **Folder URL**: ``https://your-domain.atlassian.net/wiki/spaces/MYSPACE/folder/789012?atlOrigin=...``

Note: Query parameters (``?atlOrigin=...``) are automatically ignored when parsing URLs.

Example: Include Specific Sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from docpack_confluence.api import SpaceExportConfig, ExportSpec

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="DOCS",
                include=[
                    # Export "User Guide" page and all its children
                    "https://your-domain.atlassian.net/wiki/spaces/DOCS/pages/100/User-Guide/**",
                    # Export children under "API Reference" folder (but not the folder description)
                    "https://your-domain.atlassian.net/wiki/spaces/DOCS/folder/200?atlOrigin=xxx/*",
                ],
            ),
        ],
        dir_out=Path("./docs_export"),
    )

Example: Exclude Unwanted Pages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="WIKI",
                include=[
                    # Start with all pages under "Engineering" section
                    "https://your-domain.atlassian.net/wiki/spaces/WIKI/pages/300/Engineering/**",
                ],
                exclude=[
                    # Skip the "Internal Notes" page and all its children
                    "https://your-domain.atlassian.net/wiki/spaces/WIKI/pages/400/Internal-Notes/**",
                    # Skip only direct children of "Archive" (but keep Archive page itself)
                    "https://your-domain.atlassian.net/wiki/spaces/WIKI/folder/500?atlOrigin=xxx/*",
                ],
            ),
        ],
        dir_out=Path("./wiki_export"),
    )

Filter Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The include/exclude system follows these rules:

1. **Exclude has higher priority**: If a page matches both include and exclude patterns, it will be excluded
2. **Empty include = include all**: If ``include`` is ``None`` or empty list, all pages in the space are included
3. **Empty exclude = exclude nothing**: If ``exclude`` is ``None`` or empty list, no pages are excluded

**Truth table for filtering logic:**

.. list-table::
   :header-rows: 1
   :widths: 25 25 50

   * - include
     - exclude
     - Result
   * - ``None``
     - ``None``
     - Export all pages in space
   * - ``[pattern_a]``
     - ``None``
     - Export only pages matching pattern_a
   * - ``None``
     - ``[pattern_b]``
     - Export all pages except those matching pattern_b
   * - ``[pattern_a]``
     - ``[pattern_b]``
     - Export pages matching pattern_a, but skip those also matching pattern_b


Multi-Space and Multi-Site Export
------------------------------------------------------------------------------

You can export from multiple spaces (even from different Confluence sites) in a single operation:

.. code-block:: python

    from sanhe_confluence_sdk.api import Confluence
    from docpack_confluence.api import SpaceExportConfig, ExportSpec

    # Clients for different sites
    client_team_a = Confluence(url="https://team-a.atlassian.net", ...)
    client_team_b = Confluence(url="https://team-b.atlassian.net", ...)

    spec = ExportSpec(
        space_configs=[
            # Export from Team A's documentation space
            SpaceExportConfig(
                client=client_team_a,
                space_key="DOCS",
                include=["https://team-a.atlassian.net/wiki/spaces/DOCS/pages/100/**"],
            ),
            # Export from Team A's engineering space
            SpaceExportConfig(
                client=client_team_a,
                space_id=12345,  # Can use space_id instead of space_key
                exclude=["https://team-a.atlassian.net/wiki/spaces/ENG/pages/999/Draft/**"],
            ),
            # Export from Team B's wiki
            SpaceExportConfig(
                client=client_team_b,
                space_key="WIKI",
            ),
        ],
        dir_out=Path("./multi_export"),
    )

    spec.export()

The output will have separate subdirectories for each space:

.. code-block:: text

    multi_export/
    ├── space_key_DOCS/
    │   └── ...
    ├── space_id_12345/
    │   └── ...
    ├── space_key_WIKI/
    │   └── ...
    └── all_in_one_knowledge_base.txt


Configuration Options
------------------------------------------------------------------------------

SpaceExportConfig Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Parameter
     - Default
     - Description
   * - ``client``
     - (required)
     - Confluence API client instance
   * - ``space_id``
     - ``None``
     - Space ID (mutually exclusive with ``space_key``)
   * - ``space_key``
     - ``None``
     - Space key (mutually exclusive with ``space_id``)
   * - ``include``
     - ``None``
     - List of URL patterns to include
   * - ``exclude``
     - ``None``
     - List of URL patterns to exclude
   * - ``breadcrumb_type``
     - ``title``
     - Filename format: ``"title"`` for readable names, ``"id"`` for numeric IDs
   * - ``ignore_to_markdown_error``
     - ``True``
     - Continue export if markdown conversion fails for some content

ExportSpec Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 25 20 55

   * - Parameter
     - Default
     - Description
   * - ``space_configs``
     - (required)
     - List of ``SpaceExportConfig`` objects
   * - ``dir_out``
     - (required)
     - Output directory path (will be deleted and recreated)
   * - ``encoding``
     - ``"utf-8"``
     - File encoding for output files


Common Use Cases
------------------------------------------------------------------------------

Use Case 1: Export for AI Knowledge Bases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export your documentation for AI-powered assistance. You have several options:

1. **Drag and drop**: Drop ``all_in_one_knowledge_base.txt`` directly into any AI chat interface
2. **AI platform knowledge bases**: Upload to ChatGPT Project Knowledge Base, Claude Project Files, Gemini Gems, or similar
3. **Custom vector stores**: Ingest the exported files into your own RAG pipeline or vector database

.. code-block:: python

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="DOCS",
            ),
        ],
        dir_out=Path("./ai_knowledge"),
    )
    spec.export()

    # The all-in-one file is ready for upload
    print(f"Knowledge base file: {spec.path_merged_output}")

Use Case 2: Export Specific Documentation Sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export only user-facing documentation, excluding internal notes:

.. code-block:: python

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="PRODUCT",
                include=[
                    "https://your-domain.atlassian.net/wiki/spaces/PRODUCT/pages/1/User-Manual/**",
                    "https://your-domain.atlassian.net/wiki/spaces/PRODUCT/pages/2/FAQ/**",
                    "https://your-domain.atlassian.net/wiki/spaces/PRODUCT/pages/3/Release-Notes/**",
                ],
                exclude=[
                    "https://your-domain.atlassian.net/wiki/spaces/PRODUCT/pages/999/Internal/**",
                ],
            ),
        ],
        dir_out=Path("./customer_docs"),
    )

Use Case 3: Export with ID-Based Filenames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use numeric IDs instead of titles for filenames (useful when titles contain special characters):

.. code-block:: python

    from docpack_confluence.api import BreadCrumbTypeEnum

    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="WIKI",
                breadcrumb_type=BreadCrumbTypeEnum.id,  # Files named like "123 ~ 456 ~ 789.xml"
            ),
        ],
        dir_out=Path("./id_based_export"),
    )


Content Conversion Notes
------------------------------------------------------------------------------

``docpack_confluence`` focuses on **content preservation** rather than pixel-perfect formatting. The conversion from Confluence's Atlas Doc Format to Markdown handles:

**Well Supported**:

- Headings (H1-H6)
- Paragraphs and line breaks
- Bold, italic, strikethrough, and other inline formatting
- Ordered and unordered lists
- Code blocks with syntax highlighting
- Tables (converted to Markdown tables)
- Links (internal and external)
- Blockquotes

**Partially Supported** (content preserved, formatting may differ):

- Complex nested tables
- Macros (content extracted where possible)
- Embedded media (referenced by URL)

**Not Supported** (skipped during conversion):

- Page layouts and columns
- Custom macros specific to your Confluence instance
- Interactive elements (forms, buttons, etc.)

When unsupported content is encountered, the default behavior (``ignore_to_markdown_error=True``) is to skip it gracefully and continue exporting. Set this to ``False`` if you want strict conversion that raises errors on unsupported content.


Next Steps
------------------------------------------------------------------------------

- Check out the `API Reference <https://docpack-confluence.readthedocs.io/en/latest/py-modindex.html>`_ for detailed API documentation
- Report issues or request features on `GitHub <https://github.com/MacHu-GWU/docpack_confluence-project/issues>`_
