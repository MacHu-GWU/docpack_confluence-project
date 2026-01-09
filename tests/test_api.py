# -*- coding: utf-8 -*-

from docpack_confluence import api


def test():
    _ = api
    _ = api.TAB
    _ = api.ConfluencePageFieldEnum
    _ = api.GET_PAGE_DESCENDANTS_MAX_DEPTH
    _ = api.DescendantTypeEnum
    _ = api.BreadCrumbTypeEnum
    _ = api.T_ID_PATH
    _ = api.HasRawData
    _ = api.CacheLike
    _ = api.safe_write
    _ = api.MatchMode
    _ = api.parse_pattern
    _ = api.is_match
    _ = api.Selector
    _ = api.get_space_by_id
    _ = api.get_space_by_key
    _ = api.get_pages_by_ids
    _ = api.get_pages_in_space
    _ = api.get_descendants_of_page
    _ = api.get_descendants_of_folder
    _ = api.serialize_many
    _ = api.deserialize_many
    _ = api.get_pages_in_space_with_cache
    _ = api.get_descendants_of_page_with_cache
    _ = api.get_descendants_of_folder_with_cache
    _ = api.delete_pages_and_folders_in_space
    _ = api.T_REQUEST
    _ = api.T_RESPONSE_TYPE
    _ = api.execute_with_retry
    _ = api.create_pages_and_folders
    _ = api.filter_pages
    _ = api.select_pages
    _ = api.Entity
    _ = api.crawl_descendants
    _ = api.serialize_entities
    _ = api.deserialize_entities
    _ = api.crawl_descendants_with_cache
    _ = api.export_pages_to_xml_files
    _ = api.merge_files
    _ = api.SpaceExportConfig
    _ = api.ExportSpec

if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence.api",
        preview=False,
    )
