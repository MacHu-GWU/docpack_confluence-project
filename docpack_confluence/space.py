# -*- coding: utf-8 -*-

from sanhe_confluence_sdk.api import Confluence
from sanhe_confluence_sdk.methods.space.get_spaces import (
    GetSpacesRequest,
    GetSpacesRequestQueryParams,
)
from sanhe_confluence_sdk.methods.space.get_space import (
    GetSpaceRequest,
    GetSpaceRequestPathParams,
    GetSpaceResponse,
)


def get_space_by_id(
    client: Confluence,
    space_id: int,
) -> GetSpaceResponse:
    path_params = GetSpaceRequestPathParams(id=space_id)
    request = GetSpaceRequest(path_params=path_params)
    response = request.sync(client)
    return response


def get_space_by_key(
    client: Confluence,
    space_key: str,
) -> int:
    query_params = GetSpacesRequestQueryParams(keys=[space_key])
    request = GetSpacesRequest(query_params=query_params)
    response = request.sync(client)
    space = response.results[0]
    return int(space.id)
