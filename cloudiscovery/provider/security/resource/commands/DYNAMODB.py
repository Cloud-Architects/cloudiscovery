from provider.security.command import SecurityOptions

from shared.common import (
    Resource,
    ResourceDigest,
    SecurityValues,
)


class DYNAMODB:
    def __init__(self, options: SecurityOptions):
        self.options = options

    def pitr_enabled(self, pitr_enabled):

        client = self.options.client("dynamodb")

        tables = client.list_tables()["TableNames"]

        resources_found = []

        for table in tables:
            if (
                client.describe_continuous_backups(TableName=table)[
                    "ContinuousBackupsDescription"
                ]["PointInTimeRecoveryDescription"]["PointInTimeRecoveryStatus"]
                == "DISABLED"
            ):
                resources_found.append(
                    Resource(
                        digest=ResourceDigest(id=table, type="pitr_enabled"),
                        details="PITR disabled.",
                        name=table,
                        group="ddb_security",
                        security=SecurityValues(
                            status="CRITICAL", parameter="pitr_enabled", value="False",
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
                            group="ddb_security",
                            security=SecurityValues(
                                status="CRITICAL",
                                parameter="imdsv2_check",
                                value="False",
                            ),
                        )
                    )

        return resources_found
