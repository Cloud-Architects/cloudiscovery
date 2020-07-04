from typing import List

from provider.iot.command import IotOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
    ResourceAvailable,
)
from shared.common_aws import resource_tags
from shared.error_handler import exception


class THINGS(ResourceProvider):
    def __init__(self, iot_options: IotOptions):
        """
        Iot thing

        :param iot_options:
        """
        super().__init__()
        self.iot_options = iot_options

    @exception
    @ResourceAvailable(services="iot")
    def get_resources(self) -> List[Resource]:
        client = self.iot_options.client("iot")

        resources_found = []

        if self.iot_options.verbose:
            message_handler("Collecting data from IoT Things...", "HEADER")

        for thing in self.iot_options.thing_name["things"]:
            client.describe_thing(thingName=thing["thingName"])
            tag_response = client.list_tags_for_resource(resourceArn=thing["thingArn"])

            resources_found.append(
                Resource(
                    digest=ResourceDigest(id=thing["thingName"], type="aws_iot_thing"),
                    name=thing["thingName"],
                    details="",
                    group="iot",
                    tags=resource_tags(tag_response),
                )
            )

        return resources_found


class TYPE(ResourceProvider):
    def __init__(self, iot_options: IotOptions):
        """
        Iot type

        :param iot_options:
        """
        super().__init__()
        self.iot_options = iot_options

    @exception
    @ResourceAvailable(services="iot")
    def get_resources(self) -> List[Resource]:

        client = self.iot_options.client("iot")

        resources_found = []

        if self.iot_options.verbose:
            message_handler("Collecting data from IoT Things Type...", "HEADER")

        for thing in self.iot_options.thing_name["things"]:

            response = client.describe_thing(thingName=thing["thingName"])

            thing_types = client.list_thing_types()

            for thing_type in thing_types["thingTypes"]:

                # thingTypeName is not mandatory in IoT Thing
                if "thingTypeName" in response:
                    if thing_type["thingTypeName"] == response["thingTypeName"]:
                        iot_type_digest = ResourceDigest(
                            id=thing_type["thingTypeArn"], type="aws_iot_type"
                        )
                        tag_response = client.list_tags_for_resource(
                            resourceArn=thing_type["thingTypeArn"]
                        )
                        resources_found.append(
                            Resource(
                                digest=iot_type_digest,
                                name=thing_type["thingTypeName"],
                                details="",
                                group="iot",
                                tags=resource_tags(tag_response),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=iot_type_digest,
                                to_node=ResourceDigest(
                                    id=thing["thingName"], type="aws_iot_thing"
                                ),
                            )
                        )

        return resources_found


class JOB(ResourceProvider):
    def __init__(self, iot_options: IotOptions):
        """
        Iot job

        :param iot_options:
        """
        super().__init__()
        self.iot_options = iot_options

    @exception
    @ResourceAvailable(services="iot")
    def get_resources(self) -> List[Resource]:

        client = self.iot_options.client("iot")

        resources_found = []

        if self.iot_options.verbose:
            message_handler("Collecting data from IoT Jobs...", "HEADER")

        for thing in self.iot_options.thing_name["things"]:

            client.describe_thing(thingName=thing["thingName"])

            jobs = client.list_jobs()

            for job in jobs["jobs"]:

                data_job = client.describe_job(jobId=job["jobId"])

                # Find THING name in targets things
                for target in data_job["job"]["targets"]:

                    if thing["thingName"] in target:
                        iot_job_digest = ResourceDigest(
                            id=job["jobId"], type="aws_iot_job"
                        )
                        tag_response = client.list_tags_for_resource(
                            resourceArn=job["jobArn"]
                        )
                        resources_found.append(
                            Resource(
                                digest=iot_job_digest,
                                name=job["jobId"],
                                details="",
                                group="iot",
                                tags=resource_tags(tag_response),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=iot_job_digest,
                                to_node=ResourceDigest(
                                    id=thing["thingName"], type="aws_iot_thing"
                                ),
                            )
                        )

        return resources_found


class BILLINGGROUP(ResourceProvider):
    def __init__(self, iot_options: IotOptions):
        """
        Iot billing group

        :param iot_options:
        """
        super().__init__()
        self.iot_options = iot_options

    @exception
    @ResourceAvailable(services="iot")
    def get_resources(self) -> List[Resource]:

        client = self.iot_options.client("iot")

        resources_found = []

        if self.iot_options.verbose:
            message_handler("Collecting data from IoT Billing Group...", "HEADER")

        for thing in self.iot_options.thing_name["things"]:

            response = client.describe_thing(thingName=thing["thingName"])

            billing_groups = client.list_billing_groups()

            for billing_group in billing_groups["billingGroups"]:

                # billingGroupName is not mandatory in IoT Thing
                if "billingGroupName" in response:

                    if billing_group["groupName"] == response["billingGroupName"]:
                        iot_billing_group_digest = ResourceDigest(
                            id=billing_group["groupArn"], type="aws_iot_billing_group"
                        )
                        tag_response = client.list_tags_for_resource(
                            resourceArn=billing_group["groupArn"]
                        )
                        resources_found.append(
                            Resource(
                                digest=iot_billing_group_digest,
                                name=billing_group["groupName"],
                                details="",
                                group="iot",
                                tags=resource_tags(tag_response),
                            )
                        )

                        self.relations_found.append(
                            ResourceEdge(
                                from_node=iot_billing_group_digest,
                                to_node=ResourceDigest(
                                    id=thing["thingName"], type="aws_iot_thing"
                                ),
                            )
                        )
        return resources_found
