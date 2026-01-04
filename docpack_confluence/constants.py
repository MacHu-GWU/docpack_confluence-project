# -*- coding: utf-8 -*-

"""
Constants and Enums
"""

import enum

TAB = " " * 2


class ConfluencePageFieldEnum(str, enum.Enum):
    """
    Enum for Confluence page fields.
    """

    source_type = "source_type"
    confluence_url = "confluence_url"
    title = "title"
    markdown_content = "markdown_content"
