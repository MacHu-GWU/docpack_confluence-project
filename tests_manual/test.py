from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import hierarchy_specs
from docpack_confluence.one import one
from docpack_confluence.shortcuts import (
    get_descendants_of_page_with_cache,
    delete_pages_and_folders_in_space,
    create_pages_and_folders,
)
from docpack_confluence.crawler import crawl_space_descendants
from docpack_confluence.hierarchy import enrich_pages_with_hierarchy_data

from rich import print as rprint

space_key = "DPPROJ1"  # docpack_confluence Project Space
# space = get_space_by_key(client, space_key)
# print(f"{space.id = }, {space.homepageId = }")
space_id = 654901269  # docpack_confluence Project Space
homepage_id = 654901785  # docpack_confluence Project Space homepage


def delete_all_pages_and_folders():
    """
    Delete all pages and folders in the test space.
    """
    delete_pages_and_folders_in_space(
        client=client,
        space_id=space_id,
        purge=True,
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


def test_get_descendants():
    """
    Use this function to test if the get_descendants_of_page method returns
    pages in the depth first order as expected.
    """
    descendants = get_descendants_of_page_with_cache(
        client=client,
        page_id=homepage_id,
        cache=one.cache,
    )
    for desc in descendants:
        print(f"{desc.title = }, {desc.childPosition = }")


def test_crawl_descendants():
    """Test the Parent Clustering Algorithm crawler."""
    entities = crawl_space_descendants(
        client=client,
        homepage_id=homepage_id,
        verbose=True,
    )
    for entity in entities:
        print(f"{entity.node.title = }, {entity.node.childPosition = }")


delete_all_pages_and_folders()
# create_deep_hierarchy_pages_and_folders()
# test_get_descendants()
# test_crawl_descendants()



# site_url = client.url
# pages = enrich_pages_with_hierarchy_data(
#     site_url=site_url,
#     descendant_results=descendant_results,
#     page_results=page_results,
# )
# for page in pages:
#     print(f"{page.title = }")

"""Expect:
•	Topic 1
•	topic 1 - design
•	topic 1 - design 1
•	topic 1 - design 2
•	topic 1 - document 1
•	topic 1 - document 2
•	Topic 2
•	topic 2 - document 1
•	topic 2 - document 2
•	Topic 3
•	Topic 3 Folder document
•	File 1.1.1
•	File 1.1
•	File 1.2
"""

# results = sorted(results, key=lambda r: r.position)
# for result in results:
#     print(f"{result.position = }, {result.title =}")

# include=[
#     f"{site_url}/wiki/spaces/DPPROJ/pages/653559448/Topic+1/*",
#     f"{site_url}/wiki/spaces/DPPROJ/pages/653559504/Topic+2/*",
# ]
# exclude=[
#     f"{site_url}/wiki/spaces/DPPROJ/pages/653559467/topic+1+-+design/*",
#     f"{site_url}/wiki/spaces/DPPROJ/pages/654082438/topic+1+-+document+2",
# ]

# confluence_pipeline = ConfluencePipeline(
#     confluence=confluence,
#     space_id=space_id,
#     cache_key=cache_key,
#     include=[
#         f"{confluence.url}/wiki/spaces/DOCPACKUT/pages/70647810/Topic+1/*",
#         f"{confluence.url}/wiki/spaces/DOCPACKUT/pages/70647820/Topic+2/*",
#     ],
#     exclude=[
#         f"{confluence.url}/wiki/spaces/DOCPACKUT/pages/71008257/topic+1+-+design/*",
#         f"{confluence.url}/wiki/spaces/DOCPACKUT/pages/70713375/topic+2+-+document+2",
#     ],
#     dir_out=dir_tmp,
# )
# confluence_pipeline.fetch()
