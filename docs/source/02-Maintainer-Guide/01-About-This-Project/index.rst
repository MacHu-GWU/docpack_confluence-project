.. _about-this-project:

About This Project
==============================================================================

Project Vision
------------------------------------------------------------------------------
**docpack_confluence** is a bridge between Confluence knowledge bases and AI systems. It enables seamless integration of Confluence content with any AI platform, whether through API-based systems like RAG pipelines or simple drag-and-drop file uploads to AI knowledge bases.

The core idea is simple: **make Confluence content AI-ready with minimal configuration**.


The Three Pain Points We Solve
------------------------------------------------------------------------------

1. Precise Batch Selection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Confluence is not a traditional file system. Manually specifying which pages to include is tedious and error-prone. We solve this with a familiar, low-code approach:

- **gitignore-style syntax**: Use ``include`` and ``exclude`` patterns just like ``.gitignore``
- **Hierarchical wildcards**: Use ``/*`` suffix to include a page and all its descendants
- **URL or ID support**: Specify pages using their Confluence URLs or page IDs

Example configuration::

    {
        "include": [
            "https://example.atlassian.net/wiki/spaces/KB/pages/123456/Getting+Started/*",
            "https://example.atlassian.net/wiki/spaces/KB/pages/789012/API+Reference"
        ],
        "exclude": [
            "https://example.atlassian.net/wiki/spaces/KB/pages/111111/Draft+Pages/*"
        ]
    }

This approach eliminates the need to maintain a list of individual files. Add or remove entire sections with a single pattern.

.. note::

    Currently, filtering is based on page hierarchy (parent-child relationships) using the ``/*`` syntax. Title-based filtering with DSL expressions may be added in future versions.


2. Rich Metadata Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
AI systems work best when they have context. Each exported page includes:

- **Source information**: The original Confluence URL for citation and reference
- **Page title**: For navigation and identification
- **Markdown content**: Human-readable, AI-parseable content converted from Confluence's Atlas Document Format
- **Hierarchical metadata**: Breadcrumb paths showing the page's position in the knowledge structure

The output format uses XML for metadata encapsulation with Markdown for content, providing both machine-parseability and human readability::

    <document>
      <source_type>Confluence Page</source_type>
      <confluence_url>https://example.atlassian.net/wiki/spaces/KB/pages/123/Title</confluence_url>
      <title>Page Title</title>
      <markdown_content>
    # Page Title

    Your page content in Markdown format...
      </markdown_content>
    </document>


3. Single-File Packaging
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Managing multiple files is painful for AI knowledge bases:

- **Version tracking nightmare**: Which files changed? Which need updating?
- **Sync complexity**: Uploading dozens of files is error-prone
- **Update friction**: Deleting and re-uploading many files is tedious

Our solution: **pack everything into a single file**.

- Delete the old file, upload the new one - done
- Perfect for platforms like Claude Projects, ChatGPT Knowledge, or any drag-and-drop AI system
- Works equally well with API-based RAG systems

Whether your AI platform has an API or just accepts file uploads, a single consolidated file makes synchronization trivial.


How It Works
------------------------------------------------------------------------------
1. **Configure**: Write a simple JSON configuration specifying your Confluence space and filtering rules
2. **Fetch**: The tool connects to Confluence API and retrieves matching pages
3. **Transform**: Pages are converted from Atlas Doc Format to Markdown with metadata
4. **Export**: Each page becomes a structured XML file, optionally merged into one bundle

::

    Confluence Space
         |
         v
    [Filter with include/exclude patterns]
         |
         v
    [Convert to Markdown + Metadata]
         |
         v
    Individual XML files  -->  Single packed file
                                (optional)


Use Cases
------------------------------------------------------------------------------
- **RAG Pipelines**: Feed Confluence documentation into vector databases for retrieval-augmented generation
- **AI Knowledge Bases**: Upload company wikis to Claude Projects, ChatGPT, or similar platforms
- **Documentation AI**: Create AI assistants that understand your internal documentation
- **Content Migration**: Export Confluence content in a portable, structured format


Current Limitations
------------------------------------------------------------------------------
- Page filtering is hierarchy-based only (using ``/*`` for descendants)
- Title-based filtering with DSL expressions is planned for future releases
- Requires Confluence Cloud with API access


Summary
------------------------------------------------------------------------------
**docpack_confluence** transforms Confluence from a static wiki into an AI-ready knowledge source. With simple JSON configuration and familiar gitignore-style patterns, you can:

1. **Select** exactly the pages you need
2. **Export** with rich metadata for AI consumption
3. **Package** into a single file for easy synchronization

It's the missing link between your Confluence knowledge base and the AI tools that can unlock its value.
