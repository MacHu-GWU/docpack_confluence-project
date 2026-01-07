from docpack_confluence.tests.client import client
from docpack_confluence.tests.data import hierarchy_specs
from docpack_confluence.one import one
from docpack_confluence.shortcuts import (
    get_space_by_key,
    get_pages_in_space_with_cache,
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

def delete_all():
    delete_pages_and_folders_in_space(
        client=client,
        space_id=space_id,
        purge=True,
    )


def create_deep_hierarchy():
    """
    Create a 12-level deep hierarchy with 77 nodes for testing
    the Parent Clustering Algorithm.

    Structure highlights:
    - Depth-first ordering with sequential numbering
    - Title format: p01-L1, f04-L4, p77-L12 (includes level info)
    - L4-L5: 3 clustering parents (f04, f21, p38) each with 5-6 L5 children
    - L8-L9: 3 clustering parents (f08, f25, p42) each with 4 L9 children
    - 5 branches reach L12 depth

    Total: 77 nodes (pages + folders)
    """
    create_pages_and_folders(
        client=client,
        space_id=space_id,
        hierarchy_specs=hierarchy_specs,
    )

def get_descendants():
    descendants = get_descendants_of_page_with_cache(
        client=client,
        page_id=homepage_id,
        cache=one.cache,
    )
    for desc in descendants:
        print(f"{desc.title = }, {desc.childPosition = }")
# get_descendants()

def test_crawl_descendants():
    """Test the Parent Clustering Algorithm crawler."""
    from docpack_confluence.crawler import get_node_path

    entities = crawl_space_descendants(
        client=client,
        homepage_id=homepage_id,
        verbose=True,
    )
    for entity in entities:
        print(entity.node.title)

    # Summary
    # pages = [n for n in node_pool.values() if n.type == "page"]
    # folders = [n for n in node_pool.values() if n.type == "folder"]
    # print(f"\nSummary: {len(pages)} pages, {len(folders)} folders, {len(node_pool)} total")
    #
    # # Find deepest nodes
    # max_depth = 0
    # deepest_nodes = []
    # for node_id, node in node_pool.items():
    #     path = get_node_path(node_id, node_pool)
    #     depth = len(path)
    #     if depth > max_depth:
    #         max_depth = depth
    #         deepest_nodes = [(node, path)]
    #     elif depth == max_depth:
    #         deepest_nodes.append((node, path))
    #
    # print(f"Max depth: {max_depth}")
    # print("Deepest nodes:")
    # for node, path in deepest_nodes[:3]:  # Show first 3
    #     print(f"  - {node.title}: {' -> '.join(node_pool[p].title for p in path)}")


# delete_all()
# create_deep_hierarchy()
# get_descendants()
test_crawl_descendants()
# force_refresh = True
# force_refresh = False
# descendant_results = get_descendants_of_page_with_cache(
#     client=client,
#     page_id=home_page_id,
#     cache=one.cache,
#     force_refresh=force_refresh,
# )
# page_results = get_pages_in_space_with_cache(
#     client=client,
#     space_id=space_id,
#     cache=one.cache,
#     force_refresh=force_refresh,
# )
# for result in descendant_results:
#     if result.id == "654508052":
#         rprint(result)


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
