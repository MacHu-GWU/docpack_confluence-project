# -*- coding: utf-8 -*-


import typing as T
from pathlib import Path
from sanhe_confluence_sdk.api import Confluence

from docpack_confluence.constants import DescendantTypeEnum
from docpack_confluence.shortcuts import (
    get_space_by_id,
    get_space_by_key,
    get_pages_by_ids,
    get_pages_in_space,
    filter_pages,
)
from docpack_confluence.crawler import crawl_descendants_with_cache
from docpack_confluence.page import Page
from docpack_confluence.exporter import export
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import space_id
from docpack_confluence.one import one


def main(
    dir_out: Path,
    client: Confluence,
    space_id: int = None,
    space_key: str = None,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    # wanted_fields: list[str] | None,
):
    # Get space_id
    if space_id is None:
        homepage_id = get_space_by_key(client=client, space_key=space_key).homepageId
    else:
        homepage_id = get_space_by_id(client=client, space_id=space_id).homepageId

    entities = crawl_descendants_with_cache(
        client=client,
        root_id=int(homepage_id),
        root_type=DescendantTypeEnum.page,
        cache=one.cache,
    )
    filtered_entities = filter_pages(
        entities=entities,
        include=include,
        exclude=exclude,
    )
    for entity in filtered_entities:
        print(f"{entity.title_breadcrumb_path = }")

    results = get_pages_by_ids(
        client=client,
        ids=[int(entity.node.id) for entity in filtered_entities],
    )
    result_by_id = {str(result.id): result for result in results}
    if len(filtered_entities) != len(results):
        raise ValueError("Mismatch between filtered entities and fetched pages")

    pages = []
    for entity in filtered_entities:
        result = result_by_id.get(str(entity.node.id))
        page = Page(
            site_url=client.url,
            entity=entity,
            result=result,
        )
        pages.append(page)

    export(
        pages=pages,
        dir_out=dir_out,
    )


dir_here = Path(__file__).absolute().parent
dir_out = dir_here / "tmp"


main(
    dir_out=dir_out,
    client=client,
    space_id=space_id,
    include=[
        "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/folder/655589823?atlOrigin=eyJpIjoiZWQ5ZDc4MmI1NzA3NDc4MWE3Zjg0NWZmNTZhOWM0YzgiLCJwIjoiYyJ9/*",  # f04-L4
    ],
    exclude=[
        "https://sanhehu.atlassian.net/wiki/spaces/DPPROJ1/pages/655491623/p07-L7/**",
    ],
)
