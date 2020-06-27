from shared.command import BaseCommand, CommandRunner
from shared.common import BaseAwsOptions
from shared.diagram import NoDiagram


class Limits(BaseCommand):
    def __init__(self, region_names, session, services):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param services:
        """
        super().__init__(region_names, session, False, False)
        self.services = services

    def run(self):

        for region in self.region_names:
            self.init_globalaws_limits_cache(region=region, services=self.services)
            options = BaseAwsOptions(
                session=self.session, region_name=region, services=self.services
            )

            command_runner = CommandRunner(services=self.services)
            command_runner.run(
                provider="limits",
                options=options,
                diagram_builder=NoDiagram(),
                title="AWS Limits - Region {}".format(region),
                # pylint: disable=no-member
                filename="AWS Limits - Region {}".format(region),
            )
