from unittest import TestCase

from assertpy import assert_that

from provider.all.resource.all import (
    retrieve_resource_name,
    retrieve_resource_id,
    last_singular_name_element,
)


class TestAllDiagram(TestCase):
    def test_last_singular_name_element(self):
        assert_that(last_singular_name_element("ListValues")).is_equal_to("Value")
        assert_that(last_singular_name_element("DescribeSomeValues")).is_equal_to(
            "Value"
        )

    def test_retrieve_resource_name(self):
        assert_that(
            retrieve_resource_name({"name": "value"}, "ListValues")
        ).is_equal_to("value")

        assert_that(
            retrieve_resource_name({"ValueName": "value"}, "ListValues")
        ).is_equal_to("value")
        assert_that(
            retrieve_resource_name({"SomeName": "value"}, "ListValues")
        ).is_equal_to("value")

    def test_retrieve_resource_id(self):
        assert_that(
            retrieve_resource_id({"id": "123"}, "ListValues", "value")
        ).is_equal_to("123")

        assert_that(
            retrieve_resource_id({"arn": "123"}, "ListValues", "value")
        ).is_equal_to("123")

        assert_that(
            retrieve_resource_id({"ValueName": "value"}, "ListValues", "value")
        ).is_equal_to("value")

        assert_that(
            retrieve_resource_id({"ValueId": "123"}, "ListValues", "value")
        ).is_equal_to("123")
        assert_that(
            retrieve_resource_id({"ValueArn": "123"}, "ListValues", "value")
        ).is_equal_to("123")
        assert_that(
            retrieve_resource_id({"someId": "123"}, "ListValues", "value")
        ).is_equal_to("123")
        assert_that(
            retrieve_resource_id({"someArn": "123"}, "ListValues", "value")
        ).is_equal_to("123")
