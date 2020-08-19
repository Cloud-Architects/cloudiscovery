from provider.security.command import SecurityOptions

from shared.common import (
    Resource,
    ResourceDigest,
    SecurityValues,
)


class EC2:
    def __init__(self, options: SecurityOptions):
        self.options = options

    def ebs_encryption(self, ebs_encryption):

        client = self.options.client("ec2")

        volumes = client.describe_volumes()["Volumes"]

        resources_found = []

        for volume in volumes:
            if volume["Encrypted"] is False:
                resources_found.append(
                    Resource(
                        digest=ResourceDigest(
                            id=volume["VolumeId"], type="ebs_encryption"
                        ),
                        details="This volume is not encypted.",
                        name=volume["VolumeId"],
                        group="ec2_security",
                        security=SecurityValues(
                            status="CRITICAL",
                            parameter="ebs_encryption",
                            value="False",
                        ),
                    )
                )

        return resources_found

    def imdsv2_check(self, imdsv2_check):

        client = self.options.client("ec2")

        instances = client.describe_instances()["Reservations"]

        resources_found = []

        for instance in instances:
            for instance_detail in instance["Instances"]:
                if (
                    instance_detail["MetadataOptions"]["HttpEndpoint"] == "enabled"
                    and instance_detail["MetadataOptions"]["HttpTokens"] == "optional"
                ):
                    resources_found.append(
                        Resource(
                            digest=ResourceDigest(
                                id=instance_detail["InstanceId"], type="imdsv2_check"
                            ),
                            details="IMDSv2 tokens not enforced.",
                            name=instance_detail["InstanceId"],
                            group="ec2_security",
                            security=SecurityValues(
                                status="CRITICAL",
                                parameter="imdsv2_check",
                                value="False",
                            ),
                        )
                    )

        return resources_found
