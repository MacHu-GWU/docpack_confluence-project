# -*- coding: utf-8 -*-

"""
Confluence space crawler using Parent Clustering Algorithm.

This module provides efficient fetching of complete space hierarchies,
handling the Confluence API's depth=5 limitation by clustering boundary
nodes and fetching from parent level.
"""

import typing as T
import dataclasses

# fmt: off
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.api import paginate
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequest
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestPathParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestQueryParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
# fmt: on

from .constants import GET_PAGE_DESCENDANTS_MAX_DEPTH, DescendantTypeEnum
from .shortcuts import get_descendants_of_page

# Maximum depth supported by Confluence API
MAX_DEPTH = 5


@dataclasses.dataclass(slots=True)
class Entity:
    """
    Represents a Confluence entity with its hierarchical path.

    :param lineage: List of nodes from this entity to root (reverse order).
        The first item is this entity, the last item is the root ancestor.
        Stored in reverse for efficient construction via append.
    """

    lineage: list[GetPageDescendantsResponseResult] = dataclasses.field(
        default_factory=list
    )

    @property
    def node(self) -> GetPageDescendantsResponseResult:
        """The current entity (first in the lineage)."""
        return self.lineage[0]

    @property
    def id_path(self) -> list[str]:
        """IDs from root to this entity."""
        return [n.id for n in reversed(self.lineage)]

    @property
    def title_path(self) -> list[str]:
        """Titles from root to this entity."""
        return [n.title for n in reversed(self.lineage)]

    @property
    def position_path(self) -> list[int]:
        """Child positions from root to this entity."""
        return [n.childPosition for n in reversed(self.lineage)]


def crawl_space_descendants(
    client: Confluence,
    homepage_id: int,
    verbose: bool = False,
) -> list[Entity]:
    """
    Crawl all descendants of a space using Parent Clustering Algorithm.

    Handles hierarchies deeper than 5 levels by clustering boundary nodes
    (nodes at depth=5) by their parents and fetching from parent level.
    This dramatically reduces API calls compared to naive per-node fetching.

    :param client: Authenticated Confluence API client
    :param homepage_id: ID of the space's homepage
    :param verbose: If True, print progress information

    :returns: List of Entity objects sorted by position_path (depth-first order).
        Each Entity contains the node and its lineage (path to root).

    **Algorithm**:

    1. Fetch descendants from homepage (depth=5) → get L1-L5
    2. Find boundary nodes (depth=5, meaning they might have children)
    3. For each boundary node, find its nearest PAGE ancestor
       (folders cannot be used with get_descendants API)
    4. Cluster boundary nodes by their page ancestors
    5. Fetch from each unique page ancestor (depth=5)
    6. Deduplicate (skip nodes already fetched)
    7. Repeat until no more boundary nodes
    8. Sort all entities by position_path for depth-first ordering

    **Example**::

        entities = crawl_space_descendants(client, homepage_id)

        # Entities are sorted in depth-first order by position_path
        for entity in entities:
            print(entity.node.title)
            print(entity.title_path)    # ['root', 'parent', 'child']
            print(entity.position_path) # [0, 2, 1]

        # Get all page entities
        pages = [e for e in entities if e.node.type == "page"]
    """
    # Maps node ID to Entity object (contains node and its lineage)
    node_pool: dict[str, Entity] = {}

    # Track roots to fetch from in each iteration
    # Start with homepage
    current_roots: list[int] = [homepage_id]
    iteration = 0

    while current_roots:
        iteration += 1
        if verbose:
            print(f"Iteration {iteration}: fetching from {len(current_roots)} root(s)")

        # Collect new nodes from all current roots
        new_nodes: list[GetPageDescendantsResponseResult] = []
        boundary_nodes: list[GetPageDescendantsResponseResult] = []

        for root_id in current_roots:
            for node in get_descendants_of_page(
                client=client,
                page_id=root_id,
                depth=GET_PAGE_DESCENDANTS_MAX_DEPTH,
            ):
                # Skip if already fetched (deduplication)
                if node.id in node_pool:
                    continue

                new_nodes.append(node)

                # Build lineage: [self, parent, grandparent, ..., root]
                lineage: list[GetPageDescendantsResponseResult] = [node]
                current_id = node.parentId
                while current_id in node_pool:
                    parent_entity = node_pool[current_id]
                    lineage.append(parent_entity.node)
                    current_id = parent_entity.node.parentId

                entity = Entity(lineage=lineage)
                node_pool[node.id] = entity

                # Check if this is a boundary node (at max depth relative to root)
                # These nodes might have children we haven't fetched yet
                if node.depth == MAX_DEPTH:
                    boundary_nodes.append(node)

        if verbose:
            print(
                f"  - Found {len(new_nodes)} new nodes, {len(boundary_nodes)} at boundary"
            )

        if not boundary_nodes:
            # No boundary nodes means we've reached the bottom of the hierarchy
            break

        # Parent Clustering: group boundary nodes by their nearest PAGE ancestor
        # We must use pages (not folders) because get_descendants API only works on pages
        # Instead of fetching from each boundary node individually,
        # we fetch from their nearest page ancestors
        page_ancestor_ids: set[int] = set()
        for node in boundary_nodes:
            # Walk up to find nearest page ancestor
            current_id = node.parentId
            while current_id in node_pool:
                ancestor_entity = node_pool[current_id]
                if ancestor_entity.node.type == "page":
                    page_ancestor_ids.add(int(current_id))
                    break
                current_id = ancestor_entity.node.parentId
            else:
                # No page ancestor found in node_pool, must use homepage
                # This happens when all ancestors are folders
                page_ancestor_ids.add(homepage_id)

        if verbose:
            print(
                f"  - Clustering into {len(page_ancestor_ids)} page ancestor(s) for next iteration"
            )

        # These page ancestors become the roots for the next iteration
        current_roots = list(page_ancestor_ids)

    if verbose:
        print(f"Completed: {len(node_pool)} total nodes in {iteration} iteration(s)")

    # Sort entities by position_path for depth-first ordering
    entities = list(node_pool.values())
    entities.sort(key=lambda e: e.position_path)

    return entities
