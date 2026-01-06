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
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequest
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestPathParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsRequestQueryParams
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponse
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import GetPageDescendantsResponseResult
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
