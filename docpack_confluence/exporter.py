# -*- coding: utf-8 -*-

import typing as T
import enum
import dataclasses
from pathlib import Path
from functools import cached_property

from .constants import BreadCrumbTypeEnum, ConfluencePageFieldEnum
from .utils import safe_write
from .page import Page


@dataclasses.dataclass
class Structure:
    dir_out: Path

    @cached_property
    def dir_pages(self) -> Path:
        return self.dir_out / "pages"

    @cached_property
    def path_all_in_one(self) -> Path:
        return self.dir_out / "all_in_one.txt"


def export(
    pages: T.List[Page],
    dir_out: Path,
    breadcrumb_type: BreadCrumbTypeEnum = BreadCrumbTypeEnum.title,
    wanted_fields: set[ConfluencePageFieldEnum] | None = None,
    to_markdown_ignore_error: bool = True,
    encoding: str = "utf-8",
):
    structure = Structure(dir_out=dir_out)
    lines = list()
    for page in pages:
        xml = page.to_xml(
            wanted_fields=wanted_fields,
            to_markdown_ignore_error=to_markdown_ignore_error,
        )
        lines.append(xml)
        if breadcrumb_type == BreadCrumbTypeEnum.id:
            basename = f"{page.entity.id_breadcrumb_path}.xml"
        elif breadcrumb_type == BreadCrumbTypeEnum.title:
            basename = f"{page.entity.title_breadcrumb_path}.xml"
        else:  # pragma: no cover
            raise TypeError(f"Unsupported breadcrumb_type: {breadcrumb_type}")
        path = structure.dir_pages / basename
        safe_write(path=path, content=xml, encoding=encoding)
    safe_write(
        path=structure.path_all_in_one,
        content="\n".join(lines),
        encoding=encoding,
    )
