# -*- coding: utf-8 -*-

"""
Shortcut wrappers for sanhe-confluence-sdk API with simplified parameters.
"""

import typing as T
import gzip

import orjson

# fmt: off
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.api import paginate
from sanhe_confluence_sdk.methods.model import T_RESPONSE
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceRequest
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceRequestPathParams
from sanhe_confluence_sdk.methods.space.get_space import GetSpaceResponse
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesRequest
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesRequestQueryParams
from sanhe_confluence_sdk.methods.space.get_spaces import GetSpacesResponseResult
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequest
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequestPathParams
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceRequestQueryParams
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponse
from sanhe_confluence_sdk.methods.page.get_pages_in_space import GetPagesInSpaceResponseResult
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequest
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequestPathParams
from sanhe_confluence_sdk.methods.page.delete_page import DeletePageRequestQueryParams
from sanhe_confluence_sdk.methods.page.create_page import CreatePageRequest
from sanhe_confluence_sdk.methods.page.create_page import CreatePageRequestBodyParams
from sanhe_confluence_sdk.methods.page.create_page import CreatePageResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequest
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestPathParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestQueryParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
from sanhe_confluence_sdk.methods.folder.delete_folder import DeleteFolderRequest
from sanhe_confluence_sdk.methods.folder.delete_folder import DeleteFolderRequestPathParams
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderRequest
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderRequestBodyParams
from sanhe_confluence_sdk.methods.folder.create_folder import CreateFolderResponse
# fmt: on

from diskcache import Cache


def get_space_by_id(
    client: Confluence,
    space_id: int,
) -> GetSpaceResponse:
    """
    Fetches a Confluence space by its ID.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to fetch
    """
    path_params = GetSpaceRequestPathParams(id=space_id)
    request = GetSpaceRequest(path_params=path_params)
    response = request.sync(client)
    return response


def get_space_by_key(
    client: Confluence,
    space_key: str,
) -> GetSpacesResponseResult:
    """
    Fetches a Confluence space by its key.

    :param client: Authenticated Confluence API client
    :param space_key: Key of the Confluence space to fetch
    """
    query_params = GetSpacesRequestQueryParams(keys=[space_key])
    request = GetSpacesRequest(query_params=query_params)
    response = request.sync(client)
    space = response.results[0]
    return space


def get_pages_in_space(
    client: Confluence,
    space_id: int,
    limit: int = 9999,
) -> T.Iterator[GetPagesInSpaceResponseResult]:
    """
    Crawls and retrieves all pages from a Confluence space using pagination.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to crawl
    :param limit: Number of pages to fetch

    :returns: Iterator of page results from the space
    """
    path_params = GetPagesInSpaceRequestPathParams(
        id=space_id,
    )
    query_params = GetPagesInSpaceRequestQueryParams(
        body_format="atlas_doc_format",
    )
    request = GetPagesInSpaceRequest(
        path_params=path_params,
        query_params=query_params,
    )
    paginator = paginate(
        client=client,
        request=request,
        response_type=GetPagesInSpaceResponse,
        page_size=250,
        max_items=limit,
    )
    for response in paginator:
        for result in response.results:
            yield result


def get_descendants_of_page(
    client: Confluence,
    page_id: int,
    limit: int = 9999,
) -> T.Iterator[GetPageDescendantsResponseResult]:
    """
    Crawls and retrieves all descendant pages of a given Confluence page using pagination.

    :param client: Authenticated Confluence API client
    :param page_id: ID of the Confluence page whose descendants to fetch
    :param limit: Number of descendant pages to fetch
    """
    path_params = GetPageDescendantsRequestPathParams(
        id=page_id,
    )
    query_params = GetPageDescendantsRequestQueryParams(
        depth=5,
        limit=250,
    )
    request = GetPageDescendantsRequest(
        path_params=path_params, query_params=query_params
    )
    paginator = paginate(
        client=client,
        request=request,
        response_type=GetPageDescendantsResponse,
        page_size=250,
        max_items=limit,
    )
    for response in paginator:
        for result in response.results:
            yield result


class HasRawData(T.Protocol):
    """Protocol for objects that have a raw_data attribute."""

    raw_data: dict[str, T.Any]


def serialize_many(objects: list[HasRawData]) -> bytes:
    """
    Serialize a list of objects with raw_data to gzip-compressed JSON bytes.
    """
    return gzip.compress(orjson.dumps([obj.raw_data for obj in objects]))


def deserialize_many(b: bytes, klass: T.Type[T_RESPONSE]) -> list[T_RESPONSE]:
    """
    Deserialize gzip-compressed JSON bytes back to a list of objects.
    """
    return [klass(_raw_data=data) for data in orjson.loads(gzip.decompress(b))]


def get_pages_in_space_with_cache(
    client: Confluence,
    space_id: int,
    cache: Cache,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    limit: int = 9999,
) -> list[GetPagesInSpaceResponseResult]:
    """
    Retrieves all pages from a Confluence space with disk caching.

    Uses orjson for fast serialization of raw API response data.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space to crawl
    :param cache: diskcache.Cache instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param limit: Maximum number of pages to fetch

    :returns: List of page results from the space
    """
    if cache_key is None:
        cache_key = f"get_pages_in_space@space-{space_id}"

    def fetch():
        return list(
            get_pages_in_space(
                client=client,
                space_id=space_id,
                limit=limit,
            )
        )

    def store(pages):
        cache.set(cache_key, serialize_many(pages), expire=expire)

    if force_refresh:
        pages = fetch()
        store(pages)
        return pages

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_many(cached_data, GetPagesInSpaceResponseResult)

    # Cache miss - fetch and cache
    pages = fetch()
    store(pages)
    return pages


def get_descendants_of_page_with_cache(
    client: Confluence,
    page_id: int,
    cache: Cache,
    cache_key: str | None = None,
    expire: int | None = 3600,
    force_refresh: bool = False,
    limit: int = 9999,
) -> list[GetPageDescendantsResponseResult]:
    """
    Retrieves all descendant pages of a Confluence page with disk caching.

    Uses orjson for fast serialization of raw API response data.

    :param client: Authenticated Confluence API client
    :param page_id: ID of the Confluence page whose descendants to fetch
    :param cache: diskcache.Cache instance for storing results
    :param cache_key: Manual override for cache key (auto-generated if None)
    :param expire: Cache expiration time in seconds (None for no expiration)
    :param force_refresh: If True, bypass cache and fetch fresh data
    :param limit: Maximum number of descendant pages to fetch

    :returns: List of descendant page results
    """
    if cache_key is None:
        cache_key = f"get_descendants_of_page@{page_id}"

    def fetch():
        return list(
            get_descendants_of_page(
                client=client,
                page_id=page_id,
                limit=limit,
            )
        )

    def store(pages):
        cache.set(cache_key, serialize_many(pages), expire=expire)

    if force_refresh:
        pages = fetch()
        store(pages)
        return pages

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return deserialize_many(cached_data, GetPageDescendantsResponseResult)

    # Cache miss - fetch and cache
    pages = fetch()
    store(pages)
    return pages


def delete_pages_and_folders_in_space(
    client: Confluence,
    space_id: int,
    limit: int = 9999,
) -> None:
    """
    Deletes all pages in a Confluence space.

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space whose pages to delete
    """
    space = get_space_by_id(client=client, space_id=space_id)
    for entity in get_descendants_of_page(
        client=client,
        page_id=int(space.homepageId),
        limit=limit,
    ):
        if entity.type == "page":
            path_params = DeletePageRequestPathParams(id=int(entity.id))
            query_params = DeletePageRequestQueryParams(purge=False)
            request = DeletePageRequest(
                path_params=path_params,
                query_params=query_params,
            )
            request.sync(client)
        elif entity.type == "folder":
            path_params = DeleteFolderRequestPathParams(id=int(entity.id))
            request = DeleteFolderRequest(path_params=path_params)
            request.sync(client)
        else:
            pass


def create_pages_and_folders(
    client: Confluence,
    space_id: int,
    specs: list[str],
) -> dict[str, str]:
    """
    Create pages and folders in a Confluence space based on spec strings.

    Spec format:
    - "p1" → create page with title "p1" under homepage
    - "f1" → create folder with title "f1" under homepage
    - "p2/p3" → create page with title "p3" under "p2"
    - "p2/f2" → create folder with title "f2" under "p2"

    Naming convention:
    - Starts with "p" → page
    - Starts with "f" → folder

    :param client: Authenticated Confluence API client
    :param space_id: ID of the Confluence space
    :param specs: List of spec strings (must be sorted by dependency order)

    :returns: Dictionary mapping spec key to created entity ID
    """
    space = get_space_by_id(client=client, space_id=space_id)
    homepage_id = space.homepageId

    # Sort specs to ensure parents are created before children
    specs = sorted(specs)

    # Maps title to created entity's ID
    # e.g., "p1" -> "123456", "p3" -> "789012"
    title_to_id_map: dict[str, str] = {}

    for spec in specs:
        # Parse spec: "f3/f4/p5" -> parts=["f3", "f4", "p5"]
        # - title = parts[-1] = "p5"
        # - parent = parts[-2] = "f4" (or homepage if only one part)
        parts = spec.split("/")
        title = parts[-1]

        if len(parts) == 1:
            # Root level: parent is homepage
            parent_id = homepage_id
        else:
            # Nested: parent is the second-to-last element
            parent_title = parts[-2]
            parent_id = title_to_id_map[parent_title]

        # Determine if page or folder based on prefix
        is_page = title.startswith("p")

        if is_page:
            # Create page
            body_params = CreatePageRequestBodyParams(
                space_id=str(space_id),
                parent_id=str(parent_id),
                title=title,
                body={
                    "representation": "storage",
                    "value": "",  # Empty content
                },
            )
            request = CreatePageRequest(body_params=body_params)
            response = request.sync(client)
            created_id = response.id
        else:
            # Create folder
            body_params = CreateFolderRequestBodyParams(
                space_id=str(space_id),
                parent_id=str(parent_id),
                title=title,
            )
            request = CreateFolderRequest(body_params=body_params)
            response = request.sync(client)
            created_id = response.id

        # Store title as key for nested lookups
        title_to_id_map[title] = created_id
        print(f"Created {'page' if is_page else 'folder'}: {spec} -> {created_id}")

    return title_to_id_map

