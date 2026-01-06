# -*- coding: utf-8 -*-

import typing as T

# fmt: off
from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.api import paginate
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

    :returns: List of :class:`ConfluencePage` objects with initialized page_data and site_url,
        but without hierarchy information (id_path, position_path, breadcrumb_path)
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


def get_pages_descendants(
    client: Confluence,
    page_id: int,
    limit: int = 9999,
) -> T.Iterator[GetPageDescendantsResponseResult]:
    """
    Crawls and retrieves all descendant pages of a given Confluence page using pagination.

    :param client: Authenticated Confluence API client
    :param page_id: ID of the Confluence page whose descendants
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
