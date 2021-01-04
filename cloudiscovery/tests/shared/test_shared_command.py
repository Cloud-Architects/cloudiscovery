from unittest import TestCase

from assertpy import assert_that

from shared.command import filter_resources, filter_relations
from shared.common import (
    Resource,
    ResourceDigest,
    ResourceEdge,
    Filterable,
)


class TestCommand(TestCase):
    def test_no_filters_resource(self):
        resources = filter_resources(
            [
                Resource(
                    digest=ResourceDigest(id="1", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="value")],
                )
            ],
            [],
        )

        assert_that(resources).is_length(1)
        assert_that(resources[0].digest).is_equal_to(
            ResourceDigest(id="1", type="type")
        )

    def test_one_tag_filter_resource(self):
        resources = filter_resources(
            [
                Resource(
                    digest=ResourceDigest(id="1", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="value")],
                ),
                Resource(
                    digest=ResourceDigest(id="2", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="wrong")],
                ),
            ],
            [Filterable(key="key", value="value")],
        )

        assert_that(resources).is_length(1)
        assert_that(resources[0].digest).is_equal_to(
            ResourceDigest(id="1", type="type")
        )

    def test_two_tags_filter_resource(self):
        resources = filter_resources(
            [
                Resource(
                    digest=ResourceDigest(id="1", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="value1")],
                ),
                Resource(
                    digest=ResourceDigest(id="2", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="value2")],
                ),
                Resource(
                    digest=ResourceDigest(id="3", type="type"),
                    name="name",
                    tags=[Filterable(key="key", value="wrong")],
                ),
            ],
            [
                Filterable(key="key", value="value1"),
                Filterable(key="key", value="value2"),
            ],
        )

        assert_that(resources).is_length(2).extracting(0).contains(
            ResourceDigest(id="1", type="type"), ResourceDigest(id="2", type="type")
        )

    def test_one_type_filter_resource(self):
        resources = filter_resources(
            [
                Resource(
                    digest=ResourceDigest(id="1", type="type1"),
                    name="name",
                    tags=[Filterable(key="key", value="value")],
                ),
                Resource(
                    digest=ResourceDigest(id="2", type="type2"),
                    name="name",
                    tags=[Filterable(key="key", value="wrong")],
                ),
            ],
            [Filterable(type="type1")],
        )

        assert_that(resources).is_length(1)
        assert_that(resources[0].digest).is_equal_to(
            ResourceDigest(id="1", type="type1")
        )

    def test_no_filters_relation(self):
        digest = ResourceDigest(id="1", type="type")
        edge = ResourceEdge(from_node=digest, to_node=digest)
        relations = filter_relations(
            [
                Resource(
                    digest=digest,
                    name="name",
                    tags=[Filterable(key="key", value="value")],
                )
            ],
            [edge],
        )

        assert_that(relations).is_length(1).contains(edge)

    def test_no_filtered_relation(self):
        digest = ResourceDigest(id="1", type="type")
        relations = filter_relations(
            [], [ResourceEdge(from_node=digest, to_node=digest)]
        )

        assert_that(relations).is_length(0)
