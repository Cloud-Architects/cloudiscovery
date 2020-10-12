from datetime import datetime, timedelta
import pytz

from provider.security.command import SecurityOptions

from shared.common import (
    Resource,
    ResourceDigest,
    SecurityValues,
)


class IAM:
    def __init__(self, options: SecurityOptions):
        self.options = options

    def access_keys_rotated(self, max_age):

        client = self.options.client("iam")

        users = client.list_users()

        resources_found = []

        for user in users["Users"]:
            paginator = client.get_paginator("list_access_keys")
            for keys in paginator.paginate(UserName=user["UserName"]):
                for key in keys["AccessKeyMetadata"]:

                    date_compare = datetime.utcnow() - timedelta(days=int(max_age))
                    date_compare = date_compare.replace(tzinfo=pytz.utc)
                    last_rotate = key["CreateDate"]

                    if last_rotate < date_compare:
                        resources_found.append(
                            Resource(
                                digest=ResourceDigest(
                                    id=key["AccessKeyId"], type="access_keys_rotated"
                                ),
                                details="You must rotate your keys",
                                name=key["UserName"],
                                group="iam_security",
                                security=SecurityValues(
                                    status="CRITICAL",
                                    parameter="max_age",
                                    value=str(max_age),
                                ),
                            )
                        )

        return resources_found
