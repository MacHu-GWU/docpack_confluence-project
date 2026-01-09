# -*- coding: utf-8 -*-

from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import (
    hierarchy_specs,
    space_key,
    space_id,
    homepage_id,
)
from docpack_confluence.shortcuts import (
    delete_pages_and_folders_in_space,
    create_pages_and_folders,
)
from docpack_confluence.crawler import crawl_descendants

from rich import print as rprint


def delete_all_pages_and_folders():
    """
    Delete all pages and folders in the test space.
    """
    delete_pages_and_folders_in_space(
        client=client,
        space_id=space_id,
        purge=False,
    )


def create_deep_hierarchy_pages_and_folders():
    """
    Create a 12-level deep hierarchy with 77 nodes for testing
    the Parent Clustering Algorithm.
    """
    create_pages_and_folders(
        client=client,
        space_id=space_id,
        hierarchy_specs=hierarchy_specs,
    )


def test_crawl_descendants():
    """
    Use this function to test if the get_descendants_of_page method returns
    pages in the depth first order as expected.
    """
    descendants = crawl_descendants(
        client=client,
        root_id=homepage_id,
    )
    for desc in descendants:
        print(f"{desc.node.title = }, {desc.node.childPosition = }")


# delete_all_pages_and_folders()
# create_deep_hierarchy_pages_and_folders()
# test_crawl_descendants()
