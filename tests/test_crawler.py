# -*- coding: utf-8 -*-

from docpack_confluence.crawler import (
    Entity,
    serialize_entities,
    deserialize_entities,
)
from sanhe_confluence_sdk.methods.descendant.get_page_descendants import (
    GetPageDescendantsResponseResult,
)


def test_serialize_deserialize_entities():
    p1 = GetPageDescendantsResponseResult(
        _raw_data={
            "id": "1",
            "title": "p1",
            "parentId": "0",
        }
    )
    p2 = GetPageDescendantsResponseResult(
        _raw_data={
            "id": "2",
            "title": "p2",
            "parentId": "1",
        }
    )
    p3 = GetPageDescendantsResponseResult(
        _raw_data={
            "id": "3",
            "title": "p3",
            "parentId": "2",
        }
    )
    e1 = Entity(lineage=[p1])
    e2 = Entity(lineage=[p2, p1])
    e3 = Entity(lineage=[p3, p2, p1])
    entities = [e1, e2, e3]
    data = serialize_entities(entities)
    entities_1 = deserialize_entities(data)
    assert entities == entities_1


if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence.crawler",
        preview=False,
    )
