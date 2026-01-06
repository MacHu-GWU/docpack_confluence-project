# -*- coding: utf-8 -*-

import pytest

from docpack_confluence.selector import (
    MatchMode,
    Pattern,
    Selector,
    T_ID_PATH,
    is_match,
    parse_pattern,
)


class TestMatchMode:
    def test_enum_values(self):
        assert MatchMode.SELF.value == "self"
        assert MatchMode.DESCENDANTS.value == "descendants"
        assert MatchMode.RECURSIVE.value == "recursive"

    def test_enum_is_string(self):
        assert isinstance(MatchMode.SELF, str)
        assert MatchMode.SELF == "self"


class TestPattern:
    def test_pattern_creation(self):
        pattern = Pattern(id="123", mode=MatchMode.SELF)
        assert pattern.id == "123"
        assert pattern.mode == MatchMode.SELF

    def test_pattern_frozen(self):
        pattern = Pattern(id="123", mode=MatchMode.SELF)
        with pytest.raises(Exception):  # FrozenInstanceError
            pattern.id = "456"

    def test_pattern_repr_self(self):
        pattern = Pattern(id="123", mode=MatchMode.SELF)
        assert repr(pattern) == "Pattern('123')"

    def test_pattern_repr_descendants(self):
        pattern = Pattern(id="456", mode=MatchMode.DESCENDANTS)
        assert repr(pattern) == "Pattern('456'/*)"

    def test_pattern_repr_recursive(self):
        pattern = Pattern(id="789", mode=MatchMode.RECURSIVE)
        assert repr(pattern) == "Pattern('789'/**)"


class TestParsePattern:
    """Test parse_pattern function with various URL formats."""

    def test_page_url_self_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/pages/123456/My+Page+Title"
        pattern = parse_pattern(url)
        assert pattern.id == "123456"
        assert pattern.mode == MatchMode.SELF

    def test_page_url_descendants_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/pages/123456/My+Page+Title/*"
        pattern = parse_pattern(url)
        assert pattern.id == "123456"
        assert pattern.mode == MatchMode.DESCENDANTS

    def test_page_url_recursive_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/pages/123456/My+Page+Title/**"
        pattern = parse_pattern(url)
        assert pattern.id == "123456"
        assert pattern.mode == MatchMode.RECURSIVE

    def test_page_url_without_title(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/pages/123456"
        pattern = parse_pattern(url)
        assert pattern.id == "123456"
        assert pattern.mode == MatchMode.SELF

    def test_folder_url_self_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/folder/789012?atlOrigin=xxx"
        pattern = parse_pattern(url)
        assert pattern.id == "789012"
        assert pattern.mode == MatchMode.SELF

    def test_folder_url_descendants_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/folder/789012?atlOrigin=xxx/*"
        pattern = parse_pattern(url)
        assert pattern.id == "789012"
        assert pattern.mode == MatchMode.DESCENDANTS

    def test_folder_url_recursive_mode(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/folder/789012?atlOrigin=xxx/**"
        pattern = parse_pattern(url)
        assert pattern.id == "789012"
        assert pattern.mode == MatchMode.RECURSIVE

    def test_folder_url_without_params(self):
        url = "https://example.atlassian.net/wiki/spaces/DEMO/folder/789012"
        pattern = parse_pattern(url)
        assert pattern.id == "789012"
        assert pattern.mode == MatchMode.SELF

    def test_http_url(self):
        url = "http://example.atlassian.net/wiki/spaces/DEMO/pages/123456/Title"
        pattern = parse_pattern(url)
        assert pattern.id == "123456"

    def test_invalid_url_raises_error(self):
        with pytest.raises(ValueError) as exc_info:
            parse_pattern("https://example.com/invalid/url")
        assert "Invalid Confluence URL format" in str(exc_info.value)

    def test_empty_url_raises_error(self):
        with pytest.raises(ValueError):
            parse_pattern("")


class TestIsMatch:
    """Test is_match function with various patterns and paths."""

    # Example path: p1 -> f1 -> p2 (page p2 under folder f1 under page p1)
    sample_path: T_ID_PATH = ["p1", "f1", "p2"]

    def test_empty_path_returns_false(self):
        pattern = Pattern(id="p1", mode=MatchMode.SELF)
        assert is_match(pattern, []) is False

    # SELF mode tests
    def test_self_mode_matches_current_node(self):
        pattern = Pattern(id="p2", mode=MatchMode.SELF)
        assert is_match(pattern, self.sample_path) is True

    def test_self_mode_not_matches_ancestor(self):
        pattern = Pattern(id="p1", mode=MatchMode.SELF)
        assert is_match(pattern, self.sample_path) is False

    def test_self_mode_not_matches_middle_node(self):
        pattern = Pattern(id="f1", mode=MatchMode.SELF)
        assert is_match(pattern, self.sample_path) is False

    def test_self_mode_not_matches_unknown(self):
        pattern = Pattern(id="unknown", mode=MatchMode.SELF)
        assert is_match(pattern, self.sample_path) is False

    # DESCENDANTS mode tests
    def test_descendants_mode_matches_when_ancestor(self):
        pattern = Pattern(id="p1", mode=MatchMode.DESCENDANTS)
        assert is_match(pattern, self.sample_path) is True

    def test_descendants_mode_matches_middle_ancestor(self):
        pattern = Pattern(id="f1", mode=MatchMode.DESCENDANTS)
        assert is_match(pattern, self.sample_path) is True

    def test_descendants_mode_not_matches_self(self):
        pattern = Pattern(id="p2", mode=MatchMode.DESCENDANTS)
        assert is_match(pattern, self.sample_path) is False

    def test_descendants_mode_not_matches_unknown(self):
        pattern = Pattern(id="unknown", mode=MatchMode.DESCENDANTS)
        assert is_match(pattern, self.sample_path) is False

    # RECURSIVE mode tests
    def test_recursive_mode_matches_ancestor(self):
        pattern = Pattern(id="p1", mode=MatchMode.RECURSIVE)
        assert is_match(pattern, self.sample_path) is True

    def test_recursive_mode_matches_middle(self):
        pattern = Pattern(id="f1", mode=MatchMode.RECURSIVE)
        assert is_match(pattern, self.sample_path) is True

    def test_recursive_mode_matches_self(self):
        pattern = Pattern(id="p2", mode=MatchMode.RECURSIVE)
        assert is_match(pattern, self.sample_path) is True

    def test_recursive_mode_not_matches_unknown(self):
        pattern = Pattern(id="unknown", mode=MatchMode.RECURSIVE)
        assert is_match(pattern, self.sample_path) is False

    # Single element path tests
    def test_single_element_path_self_matches(self):
        pattern = Pattern(id="root", mode=MatchMode.SELF)
        assert is_match(pattern, ["root"]) is True

    def test_single_element_path_descendants_not_matches(self):
        pattern = Pattern(id="root", mode=MatchMode.DESCENDANTS)
        assert is_match(pattern, ["root"]) is False

    def test_single_element_path_recursive_matches(self):
        pattern = Pattern(id="root", mode=MatchMode.RECURSIVE)
        assert is_match(pattern, ["root"]) is True


class TestSelector:
    """Test Selector class with include/exclude rules."""

    # Sample URLs for testing (using numeric IDs as required by Confluence)
    page_url_100 = "https://example.atlassian.net/wiki/spaces/DEMO/pages/100/Page+One"
    page_url_200 = "https://example.atlassian.net/wiki/spaces/DEMO/pages/200/Page+Two"
    page_url_300 = "https://example.atlassian.net/wiki/spaces/DEMO/pages/300/Page+Three"

    def test_empty_include_exclude_includes_all(self):
        selector = Selector(include=[], exclude=[])
        assert selector.should_include(["100", "200", "300"]) is True
        assert selector.should_include(["any", "path"]) is True

    def test_include_self_matches_exact_page(self):
        selector = Selector(include=[self.page_url_100])
        # 100 itself should be included
        assert selector.should_include(["100"]) is True
        # 200 under 100 should NOT be included (SELF mode)
        assert selector.should_include(["100", "200"]) is False

    def test_include_descendants_matches_children(self):
        url = self.page_url_100 + "/*"
        selector = Selector(include=[url])
        # 100 itself should NOT be included (DESCENDANTS mode)
        assert selector.should_include(["100"]) is False
        # 200 under 100 should be included
        assert selector.should_include(["100", "200"]) is True
        # Deeper nesting should also be included
        assert selector.should_include(["100", "200", "300"]) is True

    def test_include_recursive_matches_self_and_children(self):
        url = self.page_url_100 + "/**"
        selector = Selector(include=[url])
        # 100 itself should be included
        assert selector.should_include(["100"]) is True
        # 200 under 100 should be included
        assert selector.should_include(["100", "200"]) is True
        # Deeper nesting should also be included
        assert selector.should_include(["100", "200", "300"]) is True

    def test_exclude_overrides_include(self):
        include_url = self.page_url_100 + "/**"
        exclude_url = self.page_url_200 + "/**"
        selector = Selector(include=[include_url], exclude=[exclude_url])
        # 100 should be included
        assert selector.should_include(["100"]) is True
        # 200 under 100 should be excluded
        assert selector.should_include(["100", "200"]) is False
        # 300 under 100 (not 200) should be included
        assert selector.should_include(["100", "300"]) is True

    def test_exclude_descendants_keeps_self(self):
        include_url = self.page_url_100 + "/**"
        exclude_url = self.page_url_200 + "/*"  # Only exclude descendants
        selector = Selector(include=[include_url], exclude=[exclude_url])
        # 200 itself should be included (only its descendants are excluded)
        assert selector.should_include(["100", "200"]) is True
        # 300 under 200 should be excluded
        assert selector.should_include(["100", "200", "300"]) is False

    def test_multiple_include_patterns(self):
        url1 = self.page_url_100 + "/**"
        url2 = self.page_url_300 + "/**"
        selector = Selector(include=[url1, url2])
        # Under 100 should be included
        assert selector.should_include(["100", "child"]) is True
        # Under 300 should be included
        assert selector.should_include(["300", "child"]) is True
        # Under 200 should NOT be included
        assert selector.should_include(["200", "child"]) is False

    def test_multiple_exclude_patterns(self):
        exclude1 = self.page_url_100 + "/**"
        exclude2 = self.page_url_200 + "/**"
        selector = Selector(include=[], exclude=[exclude1, exclude2])
        # Under 100 should be excluded
        assert selector.should_include(["100", "child"]) is False
        # Under 200 should be excluded
        assert selector.should_include(["200", "child"]) is False
        # Under 300 should be included
        assert selector.should_include(["300", "child"]) is True

    def test_select_method(self):
        url = self.page_url_100 + "/**"
        selector = Selector(include=[url])

        pages = [
            ("page1", ["100"]),
            ("page2", ["100", "200"]),
            ("page3", ["300"]),  # Should be filtered out
            ("page4", ["100", "400"]),
        ]

        result = list(selector.select(pages))
        assert len(result) == 3
        assert ("page1", ["100"]) in result
        assert ("page2", ["100", "200"]) in result
        assert ("page4", ["100", "400"]) in result
        assert ("page3", ["300"]) not in result


class TestIntegrationScenarios:
    """Integration tests matching the documentation examples."""

    # Content tree from documentation (using numeric IDs):
    # 100 (p1), 100/101 (f1), 100/101/102 (p2), 100/103 (f2), 100/104 (p3), 100/104/105 (p4), 100/106 (p5)
    # 200 (f3), 200/201 (f4), 200/201/202 (p6), 200/203 (f5), 200/204 (p7), 200/204/205 (p8), 200/206 (p9)
    # 300 (p10), 400 (f6)

    base_url = "https://example.atlassian.net/wiki/spaces/DEMO"

    def make_page_url(self, page_id: str) -> str:
        return f"{self.base_url}/pages/{page_id}/Title"

    def make_folder_url(self, folder_id: str) -> str:
        return f"{self.base_url}/folder/{folder_id}?atlOrigin=xxx"

    def test_doc_example_1_export_all_under_p1(self):
        """Example 1: Export only pages under p1 (id=100)"""
        selector = Selector(include=[self.make_page_url("100") + "/**"])

        # Should include 100 (p1) and all its descendants
        assert selector.should_include(["100"]) is True
        assert selector.should_include(["100", "101", "102"]) is True  # p1/f1/p2
        assert selector.should_include(["100", "104"]) is True  # p1/p3
        assert selector.should_include(["100", "104", "105"]) is True  # p1/p3/p4
        assert selector.should_include(["100", "106"]) is True  # p1/p5

        # Should NOT include things outside 100 (p1)
        assert selector.should_include(["200", "204"]) is False  # f3/p7
        assert selector.should_include(["300"]) is False  # p10

    def test_doc_example_2_export_p1_exclude_p3_and_children(self):
        """Example 2: Export pages under p1, but exclude p3 (id=104) and its children"""
        selector = Selector(
            include=[self.make_page_url("100") + "/**"],
            exclude=[self.make_page_url("104") + "/**"],
        )

        # Should include 100 (p1), 102 (p2), 106 (p5)
        assert selector.should_include(["100"]) is True
        assert selector.should_include(["100", "101", "102"]) is True  # p1/f1/p2
        assert selector.should_include(["100", "106"]) is True  # p1/p5

        # Should exclude 104 (p3) and 105 (p4)
        assert selector.should_include(["100", "104"]) is False
        assert selector.should_include(["100", "104", "105"]) is False

    def test_doc_example_3_export_p1_exclude_only_children_of_p3(self):
        """Example 3: Export pages under p1, exclude only children of p3 (keep p3 itself)"""
        selector = Selector(
            include=[self.make_page_url("100") + "/**"],
            exclude=[self.make_page_url("104") + "/*"],  # Only descendants
        )

        # Should include 100 (p1), 102 (p2), 104 (p3), 106 (p5)
        assert selector.should_include(["100"]) is True
        assert selector.should_include(["100", "101", "102"]) is True  # p1/f1/p2
        assert selector.should_include(["100", "104"]) is True  # p3 itself is kept
        assert selector.should_include(["100", "106"]) is True  # p1/p5

        # Should exclude 105 (p4, child of p3)
        assert selector.should_include(["100", "104", "105"]) is False

    def test_doc_example_4_export_all_except_under_f3(self):
        """Example 4: Export all pages except those under f3 (id=200)"""
        selector = Selector(
            include=[],
            exclude=[self.make_folder_url("200") + "/*"],
        )

        # Should include pages not under 200 (f3)
        assert selector.should_include(["100"]) is True  # p1
        assert selector.should_include(["100", "101", "102"]) is True  # p1/f1/p2
        assert selector.should_include(["100", "104", "105"]) is True  # p1/p3/p4
        assert selector.should_include(["300"]) is True  # p10

        # Should exclude pages under 200 (f3)
        assert selector.should_include(["200", "201", "202"]) is False  # f3/f4/p6
        assert selector.should_include(["200", "204"]) is False  # f3/p7
        assert selector.should_include(["200", "204", "205"]) is False  # f3/p7/p8
        assert selector.should_include(["200", "206"]) is False  # f3/p9


if __name__ == "__main__":
    from docpack_confluence.tests import run_cov_test

    run_cov_test(
        __file__,
        "docpack_confluence.selector",
        preview=False,
    )
