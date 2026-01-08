# -*- coding: utf-8 -*-

from docpack_confluence.crawler import (
    crawl_descendants,
    crawl_descendants_with_cache,
)
from docpack_confluence.constants import DescendantTypeEnum
from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import homepage_id
from docpack_confluence.one import one

from rich import print as rprint


def test():
    descendants = crawl_descendants_with_cache(
        client=client,
        root_id=homepage_id,
        root_type=DescendantTypeEnum.page,
        cache=one.cache,
    )
    rprint(f"{len(descendants) = }")
    rprint(descendants)


if __name__ == "__main__":
    from docpack_confluence.tests import run_unit_test

    run_unit_test(__file__)
