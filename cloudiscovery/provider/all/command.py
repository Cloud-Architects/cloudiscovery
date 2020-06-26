from shared.command import BaseCommand, CommandRunner
from shared.common import BaseAwsOptions
from shared.diagram import NoDiagram


class All(BaseCommand):
    def __init__(self, region_names, session, filters):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param filters:
        """
        super().__init__(region_names, session, False, filters)

    def run(self):
        for region in self.region_names:
            self.init_region_cache(region)
            options = BaseAwsOptions(session=self.session, region_name=region)

            command_runner = CommandRunner(self.filters)
            command_runner.run(
                provider="all",
                options=options,
                diagram_builder=NoDiagram(),
                title="AWS Resources - Region {}".format(region),
                filename=options.resulting_file_name("all"),
            )
