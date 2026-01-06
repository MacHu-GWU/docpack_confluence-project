from docpack_confluence.tests.client import client
from docpack_confluence.one import one
from docpack_confluence.shortcuts import (
    get_space_by_key,
    get_pages_in_space_with_cache,
    get_descendants_of_page_with_cache,
    delete_pages_and_folders_in_space,
    create_pages_and_folders,
)
from docpack_confluence.hierarchy import enrich_pages_with_hierarchy_data
from rich import print as rprint

space_key = "DPPROJ1"  # docpack_confluence Project Space
# space = get_space_by_key(client, space_key)
# print(f"{space.id = }, {space.homepageId = }")
space_id = 654901269  # docpack_confluence Project Space
home_page_id = 654901785  # docpack_confluence Project Space homepage

def delete_all():
    delete_pages_and_folders_in_space(
        client=client,
        space_id=space_id,
    )


def create_deep_hierarchy():
    """
    Create a 12-level deep hierarchy with ~76 nodes for testing
    the Parent Clustering Algorithm.

    Structure highlights:
    - L4-L5: 3 parent folders (f008, f009, f010) each with 5-8 children
    - L8-L9: 3 parent folders (f040, f041, f042) each with 4-5 children
    - This creates clustering-friendly scenarios where many L5/L9 boundary
      nodes share few L4/L8 parents

    Total: 76 nodes (pages + folders)
    """
    # Renamed from 'specs' to 'hierarchy_specs' for clarity
    # Full paths shown for human readability (only last 2 parts are used by code)
    hierarchy_specs = [
        # === L1: 2 nodes (under homepage) ===
        "p001",
        "f001",
        # === L2: 4 nodes ===
        "p001/p002",
        "p001/f002",
        "f001/p003",
        "f001/f003",
        # === L3: 8 nodes ===
        "p001/p002/p004",
        "p001/p002/f004",
        "p001/f002/p005",
        "p001/f002/f005",
        "f001/p003/p006",
        "f001/p003/f006",
        "f001/f003/p007",
        "f001/f003/f007",
        # === L4: 7 nodes (3 are clustering parents for L5) ===
        "p001/p002/p004/f008",  # clustering parent - will have 8 L5 children
        "p001/f002/f005/f009",  # clustering parent - will have 6 L5 children
        "f001/f003/f007/f010",  # clustering parent - will have 6 L5 children
        "p001/p002/f004/p008",
        "p001/f002/p005/f011",
        "f001/p003/p006/p009",
        "f001/p003/f006/p010",
        # === L5: 20 nodes (clustering-friendly: many children under few parents) ===
        # Under f008: 8 children
        "p001/p002/p004/f008/p020",
        "p001/p002/p004/f008/p021",
        "p001/p002/p004/f008/p022",
        "p001/p002/p004/f008/p023",
        "p001/p002/p004/f008/f020",
        "p001/p002/p004/f008/f021",
        "p001/p002/p004/f008/f022",
        "p001/p002/p004/f008/f023",
        # Under f009: 6 children
        "p001/f002/f005/f009/p024",
        "p001/f002/f005/f009/p025",
        "p001/f002/f005/f009/p026",
        "p001/f002/f005/f009/f024",
        "p001/f002/f005/f009/f025",
        "p001/f002/f005/f009/f026",
        # Under f010: 6 children
        "f001/f003/f007/f010/p027",
        "f001/f003/f007/f010/p028",
        "f001/f003/f007/f010/p029",
        "f001/f003/f007/f010/f027",
        "f001/f003/f007/f010/f028",
        "f001/f003/f007/f010/f029",
        # === L6: 4 nodes ===
        "p001/p002/p004/f008/p020/p030",
        "p001/p002/p004/f008/p020/f030",
        "p001/f002/f005/f009/p024/p031",
        "f001/f003/f007/f010/p027/f031",
        # === L7: 4 nodes ===
        "p001/p002/p004/f008/p020/p030/p032",
        "p001/p002/p004/f008/p020/f030/p033",
        "p001/f002/f005/f009/p024/p031/f032",
        "f001/f003/f007/f010/p027/f031/p034",
        # === L8: 4 nodes (3 are clustering parents for L9) ===
        "p001/p002/p004/f008/p020/p030/p032/f040",  # clustering parent
        "p001/p002/p004/f008/p020/f030/p033/f041",  # clustering parent
        "p001/f002/f005/f009/p024/p031/f032/f042",  # clustering parent
        "f001/f003/f007/f010/p027/f031/p034/p035",
        # === L9: 14 nodes (clustering-friendly: many children under few parents) ===
        # Under f040: 5 children
        "p001/p002/p004/f008/p020/p030/p032/f040/p050",
        "p001/p002/p004/f008/p020/p030/p032/f040/p051",
        "p001/p002/p004/f008/p020/p030/p032/f040/p052",
        "p001/p002/p004/f008/p020/p030/p032/f040/f050",
        "p001/p002/p004/f008/p020/p030/p032/f040/f051",
        # Under f041: 4 children
        "p001/p002/p004/f008/p020/f030/p033/f041/p053",
        "p001/p002/p004/f008/p020/f030/p033/f041/p054",
        "p001/p002/p004/f008/p020/f030/p033/f041/f052",
        "p001/p002/p004/f008/p020/f030/p033/f041/f053",
        # Under f042: 4 children
        "p001/f002/f005/f009/p024/p031/f032/f042/p055",
        "p001/f002/f005/f009/p024/p031/f032/f042/p056",
        "p001/f002/f005/f009/p024/p031/f032/f042/f054",
        "p001/f002/f005/f009/p024/p031/f032/f042/f055",
        # Leaf at L9
        "f001/f003/f007/f010/p027/f031/p034/p035/p057",
        # === L10: 3 nodes ===
        "p001/p002/p004/f008/p020/p030/p032/f040/p050/p060",
        "p001/p002/p004/f008/p020/f030/p033/f041/p053/f060",
        "p001/f002/f005/f009/p024/p031/f032/f042/p055/p061",
        # === L11: 3 nodes ===
        "p001/p002/p004/f008/p020/p030/p032/f040/p050/p060/p070",
        "p001/p002/p004/f008/p020/f030/p033/f041/p053/f060/p071",
        "p001/f002/f005/f009/p024/p031/f032/f042/p055/p061/f070",
        # === L12: 3 nodes (deepest level) ===
        "p001/p002/p004/f008/p020/p030/p032/f040/p050/p060/p070/p080",
        "p001/p002/p004/f008/p020/f030/p033/f041/p053/f060/p071/p081",
        "p001/f002/f005/f009/p024/p031/f032/f042/p055/p061/f070/p082",
    ]

    create_pages_and_folders(
        client=client,
        space_id=space_id,
        hierarchy_specs=hierarchy_specs,
    )

# delete_all()
# create_deep_hierarchy()

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
