from typing import List

from provider.iot.command import IotOptions
from shared.common import (
    ResourceProvider,
    Resource,
    message_handler,
    ResourceDigest,
    ResourceEdge,
)
from shared.error_handler import exception


class POLICY(ResourceProvider):
    def __init__(self, iot_options: IotOptions):
        """

        :param iot_options:
        """
        super().__init__()
        self.iot_options = iot_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.iot_options.client("iot")

        resources_found = []

        message_handler("Collecting data from IoT Policies...", "HEADER")

        for thing in self.iot_options.thing_name["things"]:

            response = client.list_thing_principals(thingName=thing["thingName"])

            for data in response["principals"]:

                policies = client.list_principal_policies(principal=data)

                for policy in policies["policies"]:
                    data_policy = client.get_policy(policyName=policy["policyName"])

                    iot_policy_digest = ResourceDigest(
                        id=data_policy["policyArn"], type="aws_iot_policy"
                    )
                    resources_found.append(
                        Resource(
                            digest=iot_policy_digest,
                            name=data_policy["policyName"],
                            details="",
                            group="iot",
                        )
                    )

                    self.relations_found.append(
                        ResourceEdge(
                            from_node=iot_policy_digest,
                            to_node=ResourceDigest(
                                id=thing["thingName"], type="aws_iot_thing"
                            ),
                        )
                    )

        return resources_found
