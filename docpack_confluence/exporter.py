# -*- coding: utf-8 -*-

import typing as T
import shutil
from pathlib import Path

from .constants import BreadCrumbTypeEnum, ConfluencePageFieldEnum
from .utils import safe_write
from .page import Page


def export(
    pages: T.List[Page],
    dir_out: Path,
    breadcrumb_type: BreadCrumbTypeEnum = BreadCrumbTypeEnum.title,
    wanted_fields: set[ConfluencePageFieldEnum] | None = None,
    to_markdown_ignore_error: bool = True,
    encoding: str = "utf-8",
    remove_dir_out_if_exists: bool = False,
):
    if remove_dir_out_if_exists:
        shutil.rmtree(dir_out, ignore_errors=True)
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
        path = dir_out / basename
        safe_write(path=path, content=xml, encoding=encoding)


def concatenate_files_in_folder_to_one(
    dir_in: Path,
    path_out: Path,
    input_encoding: str = "utf-8",
    output_encoding: str = "utf-8",
    overwrite: bool = True,
):
    if overwrite is False:
        if path_out.exists():
            raise FileExistsError(f"File already exists: {path_out}")
    paths = list(dir_in.glob("**/*.*"))
    lines = [path.read_text(encoding=input_encoding) for path in paths]
    safe_write(
        path=path_out,
        content="\n".join(lines),
        encoding=output_encoding,
    )
