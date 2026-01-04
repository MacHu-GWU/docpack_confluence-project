---
name: dev
description: Maintainer guide for docpack_confluence development. Use when understanding project architecture, implementing features, or learning the codebase.
---

# docpack_confluence Maintainer Guide

This skill provides guidance for developing and maintaining the docpack_confluence library.

## Available Topics

Read the specific document when you need detailed information:

| Topic | Document | When to Read |
|-------|----------|--------------|
| **Project Overview** | [01-About-This-Project](docs/source/02-Maintainer-Guide/01-About-This-Project/index.rst) | Understanding project vision, pain points solved, and use cases |

## Quick Reference

- **Understand the project**: Read "Project Overview" first
- **Learn the architecture**: (TODO: add architecture doc)
- **Implement new features**: (TODO: add implementation guide)
- **Write tests**: (TODO: add testing guide)

## Core Concepts

### The Three Pain Points

1. **Precise Batch Selection**: gitignore-style `include`/`exclude` patterns with `/*` wildcards
2. **Rich Metadata Output**: XML-wrapped Markdown with source URLs and hierarchical metadata
3. **Single-File Packaging**: Consolidate all pages into one file for easy AI platform sync

### Key Components

- `ConfluencePage`: Data model for enriched page content
- `ConfluencePipeline`: Main workflow orchestrator
- Filter functions: `extract_id`, `is_matching`, `find_matching_pages`
- Fetcher functions: `fetch_raw_pages_from_space`, `enrich_pages_with_hierarchy_data`

## Related Skills

(Add related skills here as needed)
