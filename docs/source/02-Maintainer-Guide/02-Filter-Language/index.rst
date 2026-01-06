.. _filter-language:

Filter Language
==============================================================================

This document defines the filter language for selecting Confluence pages to export.


Confluence Content Model
------------------------------------------------------------------------------

In Confluence Cloud, there are two types of content entities:

- **Page**: Contains text content and can have child nodes (acts as both content and directory)
- **Folder**: Cannot contain text content, only acts as a directory for organizing other content

Both Page and Folder have:

- A unique ``id``
- A nullable ``parent_id`` (root-level items have ``parent_id`` = Space's ``homepage_id``)

**Example content tree**::

    p1              # Page at root level
    p1/f1           # Folder under p1
    p1/f1/p2        # Page under f1
    p1/f2           # Folder under p1
    p1/p3           # Page under p1
    p1/p3/p4        # Page under p3
    p1/p5           # Page under p1
    f3              # Folder at root level
    f3/f4           # Folder under f3
    f3/f4/p6        # Page under f4
    f3/f5           # Folder under f3
    f3/p7           # Page under f3
    f3/p7/p8        # Page under p7
    f3/p9           # Page under f3
    p10             # Page at root level
    f6              # Folder at root level (empty)

Where ``p`` = Page, ``f`` = Folder.


Filter Rules
------------------------------------------------------------------------------

The filter system uses two lists:

- **include**: Specifies which pages to include
- **exclude**: Specifies which pages to exclude

**Priority**: ``exclude`` > ``include``. If a page matches both lists, it is excluded.

**Default behavior**:

- ``include: []`` (empty list) = Include ALL pages in the space
- ``exclude: []`` (empty list) = Exclude nothing

.. note::

    The filter only returns **Pages**. Folders are never included in the output
    because they have no content to export.


URL-Based Matching Syntax
------------------------------------------------------------------------------

Filters use Confluence URLs to identify content nodes:

**Page URL format**::

    https://{domain}/wiki/spaces/{space_key}/pages/{page_id}/{title-slug}

    Example: https://example.atlassian.net/wiki/spaces/DEMO/pages/653559448/My+Page+Title

**Folder URL format**::

    https://{domain}/wiki/spaces/{space_key}/folder/{folder_id}?{params}

    Example: https://example.atlassian.net/wiki/spaces/DEMO/folder/653559520?atlOrigin=xxx

**Matching rules**:

- Only ``{page_id}`` or ``{folder_id}`` is used for identification
- Everything after the ID (title slug, query params) is **ignored**
- To add wildcards, append ``/*`` or ``/**`` at the end of the URL


Wildcard Syntax
------------------------------------------------------------------------------

Three matching modes are supported:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Syntax
     - Meaning
     - Example Result
   * - ``{url}``
     - Match only this node itself
     - ``p1`` → only p1
   * - ``{url}/*``
     - Match all descendants (excluding the node itself)
     - ``p1/*`` → p2, p3, p4, p5
   * - ``{url}/**``
     - Match this node AND all descendants
     - ``p1/**`` → p1, p2, p3, p4, p5

**Important notes**:

- Descendants are matched **recursively** (all levels, not just direct children)
- When matching a **Folder** without wildcard, the result is empty (folders have no content)
- When matching a **Folder** with ``/*`` or ``/**``, only the **Pages** under it are returned


Matching Examples
------------------------------------------------------------------------------

Using the example content tree above:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Filter
     - Matched Pages
   * - ``p1``
     - p1
   * - ``p1/*``
     - p2, p3, p4, p5 (all pages under p1, excluding p1 itself)
   * - ``p1/**``
     - p1, p2, p3, p4, p5 (p1 and all pages under it)
   * - ``f3``
     - *(empty)* - f3 is a folder, no content to match
   * - ``f3/*``
     - p6, p7, p8, p9 (all pages under f3, recursively)
   * - ``f3/**``
     - p6, p7, p8, p9 (same as above, f3 itself is a folder so not included)
   * - ``f4/*``
     - p6 (only page under f4)
   * - ``p3/*``
     - p4 (only page under p3)
   * - ``p3/**``
     - p3, p4


Include/Exclude Combination Examples
------------------------------------------------------------------------------

**Example 1**: Export only pages under p1

.. code-block:: yaml

    include:
      - "https://example.atlassian.net/wiki/spaces/DEMO/pages/p1/Page+One/**"
    exclude: []

Result: p1, p2, p3, p4, p5

**Example 2**: Export pages under p1, but exclude p3 and its children

.. code-block:: yaml

    include:
      - "https://example.atlassian.net/wiki/spaces/DEMO/pages/p1/Page+One/**"
    exclude:
      - "https://example.atlassian.net/wiki/spaces/DEMO/pages/p3/Page+Three/**"

Result: p1, p2, p5

**Example 3**: Export pages under p1, exclude only children of p3 (keep p3 itself)

.. code-block:: yaml

    include:
      - "https://example.atlassian.net/wiki/spaces/DEMO/pages/p1/Page+One/**"
    exclude:
      - "https://example.atlassian.net/wiki/spaces/DEMO/pages/p3/Page+Three/*"

Result: p1, p2, p3, p5

**Example 4**: Export all pages except those under f3

.. code-block:: yaml

    include: []  # empty = include all
    exclude:
      - "https://example.atlassian.net/wiki/spaces/DEMO/folder/f3?atlOrigin=xxx/*"

Result: p1, p2, p3, p4, p5, p10
