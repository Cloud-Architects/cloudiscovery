from unittest import TestCase

from assertpy import assert_that

from shared.common import parse_filters, Filterable


class TestCommon(TestCase):
    def test_parse_filters_simple_tag_filter(self):
        filters = parse_filters(["Name=tags.costCenter;Value=20000"])
        assert_that(filters).is_length(1)
        assert_that(filters).contains(Filterable(key="costCenter", value="20000"))

    def test_parse_filters_type_filter(self):
        filters = parse_filters(["Name=type;Value=aws_lambda_function"])
        assert_that(filters).is_length(1)
        assert_that(filters).contains(Filterable(type="aws_lambda_function"))

    def test_parse_filters_wrong_filter(self):
        filters = parse_filters(["Name=wrong;Value=value"])
        assert_that(filters).is_length(0)

    def test_parse_filters_two_values_tag_filter(self):
        filters = parse_filters(["Name=tags.costCenter;Value=20000:20001"])
        assert_that(filters).is_length(2)
        assert_that(filters).contains(Filterable(key="costCenter", value="20000"))
        assert_that(filters).contains(Filterable(key="costCenter", value="20001"))

    def test_parse_filters_two_complex_values_tag_filter(self):
        filters = parse_filters(["Name=tags.costCenter;Value=20000:'20000:1'"])
        assert_that(filters).is_length(2)
        assert_that(filters).contains(Filterable(key="costCenter", value="20000"))
        assert_that(filters).contains(Filterable(key="costCenter", value="20000:1"))

    def test_parse_filters_invalid_tag_parts_filter(self):
        filters = parse_filters(["Name=tags.;costCenter;Value=20000"])
        assert_that(filters).is_length(0)

    def test_parse_filters_invalid_tag_name_filter(self):
        filters = parse_filters(["nn=tags.costCenter;Value=20000"])
        assert_that(filters).is_length(0)

    def test_parse_filters_invalid_tag_value_filter(self):
        filters = parse_filters(["Name=tags.costCenter;vvv20000"])
        assert_that(filters).is_length(0)
