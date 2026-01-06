# -*- coding: utf-8 -*-

"""
Confluence page fetching and processing utilities.
"""

# fmt: off
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponseResult
# fmt: on

from .page import Page


def enrich_pages_with_hierarchy_data(
    site_url: str,
    descendant_results: list[GetPageDescendantsResponseResult],
    page_results: list[GetPagesInSpaceResponseResult],
) -> list[Page]:
    """
    Enriches Confluence page objects with hierarchical relationship information.

    This function processes a list of raw ConfluencePage objects to:

    1. Create ID-based paths (id_path) representing the page hierarchy
    2. Generate position-based paths (position_path) for correct sorting
    3. Build human-readable title hierarchies (breadcrumb_path) for display

    The function creates a complete hierarchy tree by iteratively processing pages
    for up to 20 levels of depth, starting with parent pages and moving to children.

    :param raw_pages: List of :class:`ConfluencePage` objects with basic data but no hierarchy info

    :returns: List of :class:`ConfluencePage` objects enriched with hierarchy data and sorted by
        their position in the hierarchy
    """
    # Create a mapping of page IDs to page objects for quick lookups
    id_to_result_mapping: dict[str, GetPagesInSpaceResponseResult] = {
        result.id: result for result in page_results
    }
    id_to_ancestors_mapping: dict[str, list[str]] = dict()
    # def set_ancestors(result: GetPagesInSpaceResponseResult):
    #     try:

    # Create a working copy of the mapping to track unprocessed pages
    remaining_results = dict(id_to_result_mapping)

    # Limit recursion depth to avoid infinite loops with circular references
    max_next_level = 20

    # Process pages level by level, starting from root pages
    # 因为原生 API 并没有按照层级顺序返回页面，所以我们必须要在内存中暴力多次遍历而不能用深度优先
    # 算法建立层级关系
    for ith in range(1, 1 + max_next_level):
        msg = (
            f"=== {ith = }, "
            f"{len(remaining_results) = }, "
            f"{len(id_to_ancestors_mapping) = }"
        )
        # print(msg) # for debug only
        # Exit if all pages have been processed
        if len(remaining_results) == 0:
            break

        # Process each remaining page
        for id, result in list(remaining_results.items()):
            # Process root pages (no parent or parent outside our space)
            if result.parentId is None:
                # Create hierarchy paths for root pages
                ancestors = []
                id_to_ancestors_mapping[id] = ancestors
                # path = f"/{result.id}"
                # sort_key = f"/{result.position}"
                # title_chain = f"|| {result.title}"
                # result.id_path = path
                # result.position_path = sort_key
                # result.breadcrumb_path = title_chain
                # Remove from remaining pages as it's now processed
                remaining_results.pop(result.id)

            # Process child pages
            else:
                # Check if the parent page is in our collection
                if result.parentId in id_to_result_mapping:
                    parent_result = id_to_result_mapping[result.parentId]
                    # Skip if parent's paths aren't set yet (will process in later iteration)
                    if parent_result.id not in id_to_ancestors_mapping:
                        continue

                    # Create hierarchy paths based on parent's paths
                    parent_ancestors = list(id_to_ancestors_mapping[parent_result.id])
                    ancestors = parent_ancestors
                    ancestors.append(parent_result.id)
                    id_to_ancestors_mapping[id] = ancestors

                    # Remove from remaining pages as it's now processed
                    remaining_results.pop(id)

                # Handle pages with parents outside our scope (typically Confluence folders)
                else:
                    # Remove these pages from both mappings as they can't be processed
                    remaining_results.pop(id)
                    id_to_result_mapping.pop(id)

    #
    if len(id_to_ancestors_mapping) != len(id_to_result_mapping):
        raise ValueError

    id_to_page_mapping: dict[str, Page] = dict()
    for id, ancestors in id_to_ancestors_mapping.items():
        result = id_to_result_mapping[id]
        page = Page(
            _raw_data=result.raw_data,
            site_url=site_url,
            ancestors=[id_to_page_mapping[_id] for _id in ancestors],
        )
        id_to_page_mapping[id] = page

    # Sort pages based on their positions in the hierarchy
    sorted_pages = list(
        sorted(
            id_to_page_mapping.values(),
            key=lambda page: page.sort_key,
        )
    )

    return sorted_pages
