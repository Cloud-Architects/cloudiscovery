from typing import List

from shared.command import BaseCommand, CommandRunner
from shared.common import BaseAwsOptions
from shared.diagram import NoDiagram
from shared.common_aws import ALLOWED_SERVICES_CODES


class LimitOptions(BaseAwsOptions):
    services: List[str]

    def __new__(cls, session, region_name, services, usage):
        """
        Limit Options

        :param session:
        :param region_name:
        :param services:
        """
        self = super(BaseAwsOptions, cls).__new__(cls, (session, region_name))
        self.services = services
        self.usage = usage
        return self


class Limit(BaseCommand):
    def __init__(self, region_names, session, services, usage):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param services:
        """
        super().__init__(region_names, session, False, False)
        self.services = []
        if services is None:
            for service in ALLOWED_SERVICES_CODES:
                self.services.append(service)
        else:
            self.services = services.split(",")

        self.usage = usage

    def run(self):

        for region in self.region_names:
            self.init_globalaws_limits_cache(region=region, services=self.services)
            limit_options = LimitOptions(
                session=self.session,
                region_name=region,
                services=self.services,
                usage=self.usage,
            )

            command_runner = CommandRunner(services=self.services)
            command_runner.run(
                provider="limit",
                options=limit_options,
                diagram_builder=NoDiagram(),
                title="AWS Limits - Region {}".format(region),
                # pylint: disable=no-member
                filename=limit_options.resulting_file_name("limit"),
            )
