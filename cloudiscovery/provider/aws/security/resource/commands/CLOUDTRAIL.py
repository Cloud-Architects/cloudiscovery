from provider.aws.security.command import SecurityOptions

from shared.common import (
    Resource,
    ResourceDigest,
    SecurityValues,
)


class CLOUDTRAIL:
    def __init__(self, options: SecurityOptions):
        self.options = options

    def cloudtrail_enabled(self, cloudtrail_enabled):

        client = self.options.client("cloudtrail")

        trails = client.list_trails()

        resources_found = []

        if not trails["Trails"]:
            resources_found.append(
                Resource(
                    digest=ResourceDigest(id="cloudtrail", type="cloudtrail_enabled"),
                    details="CLOUDTRAIL disabled",
                    name="cloudtrail",
                    group="cloudtrail_security",
                    security=SecurityValues(
                        status="CRITICAL",
                        parameter="cloudtrail_enabled",
                        value="False",
                    ),
                )
            )

        return resources_found
