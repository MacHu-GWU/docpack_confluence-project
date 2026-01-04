# -*- coding: utf-8 -*-

"""
Confluence page fetching and processing utilities.
"""

import typing as T
import json
import dataclasses
from functools import cached_property

from func_args.api import REQ
import atlas_doc_parser.api as atlas_doc_parser
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponseResult

from .constants import TAB, ConfluencePageFieldEnum


@dataclasses.dataclass(frozen=True)
class Page(GetPagesInSpaceResponseResult):
    """
    A data container for Confluence pages that enriches the API response data with
    hierarchical metadata and navigation properties.

    This class wraps the raw page data returned by Confluence's
    `get pages <https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-get>`_ API
    and adds additional attributes for working with page hierarchies and navigation.

    :param page_data: The raw item response from the `Confluence.get_pages` API call
    :param site_url: Base URL of the Confluence site
    :param id_path: Hierarchical ID-based path (e.g., "/parent_id/child_id")
        for filtering with glob patterns
    :param position_path: Position-based path (e.g., "/1/3/2") used for hierarchical sorting
    :param breadcrumb_path: Human-readable title hierarchy (e.g., "|| Parent || Child || Page")
        similar to UI breadcrumbs

    The class assumes the body format is
    `Atlas Doc Format <https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/>`_

    Properties like `id`, `title`, `parent_id` provide convenient access to commonly
    used attributes from the raw page data.
    """
    # id_path: str = REQ
    # position_path: str = REQ
    # breadcrumb_path: str = REQ
    site_url: str = dataclasses.field(default=REQ)
    ancestors: list["Page"] = dataclasses.field(default_factory=list)

    @cached_property
    def atlas_doc(self) -> dict[str, T.Any]:
        return json.loads(self.body.atlas_doc_format.value)

    @cached_property
    def _formatted_site_url(self) -> str:
        if self.site_url.endswith("/"):
            return self.site_url[:-1]
        else:
            return self.site_url

    @cached_property
    def webui_url(self) -> str:
        return f"{self._formatted_site_url}/wiki{self.links.webui}"

    def to_markdown(self, ignore_error: bool = True) -> str:
        node_doc = atlas_doc_parser.NodeDoc.from_dict(
            dct=self.atlas_doc,
        )
        md = node_doc.to_markdown(ignore_error=ignore_error)
        lines = [
            f"# {self.title}",
            "",
        ]
        lines.extend(md.splitlines())
        md = "\n".join(lines)
        return md

    def to_xml(
        self,
        wanted_fields: set[ConfluencePageFieldEnum] | None = None,
        to_markdown_ignore_error: bool = True,
    ) -> str:
        """
        Serialize the file data to XML format.

        This method generates an XML representation of the file including its GitHub
        metadata and content, suitable for document storage or AI context input.
        """
        if wanted_fields is None:
            wanted_fields = {field.value for field in ConfluencePageFieldEnum}
        else:
            wanted_fields = {field.value for field in wanted_fields}
        lines = list()
        lines.append("<document>")

        field = ConfluencePageFieldEnum.source_type.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>Confluence Page</{field}>")

        field = ConfluencePageFieldEnum.confluence_url.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>{self.webui_url}</{field}>")

        field = ConfluencePageFieldEnum.title.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>{self.title}</{field}>")

        field = ConfluencePageFieldEnum.markdown_content.value
        if field in wanted_fields:
            lines.append(f"{TAB}<{field}>")
            lines.append(self.to_markdown(ignore_error=to_markdown_ignore_error))
            lines.append(f"{TAB}</{field}>")

        lines.append("</document>")

        return "\n".join(lines)

    # def export_to_file(
    #     self,
    #     dir_out: Path,
    #     wanted_fields: list[str] | None = None,
    # ) -> Path:
    #     fname = self.breadcrumb_path[3:].replace("||", "~")
    #     basename = f"{fname}.xml"
    #     path_out = dir_out.joinpath(basename)
    #     content = self.to_xml(wanted_fields=wanted_fields)
    #     try:
    #         path_out.write_text(content, encoding="utf-8")
    #     except FileNotFoundError:
    #         path_out.parent.mkdir(parents=True)
    #         path_out.write_text(content, encoding="utf-8")
    #     return path_out
