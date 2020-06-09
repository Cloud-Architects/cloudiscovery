from shared.command import BaseCommand, CommandRunner
from shared.common import BaseOptions
from shared.diagram import NoDiagram, BaseDiagram


class Policy(BaseCommand):
    def __init__(self, region_names, session, diagram):
        """
        Policy

        :param region_names:
        :param session:
        :param diagram:
        """
        super().__init__(region_names, session, diagram)

    def run(self):
        for region in self.region_names:

            command_runner = CommandRunner()
            if self.diagram:
                diagram = BaseDiagram(
                    "AWS Permissions map", region + "_account_policies", engine="fdp"
                )
            else:
                diagram = NoDiagram()
            options = BaseOptions(session=self.session, region_name=region)
            command_runner.run(
                provider="policy",
                options=options,
                diagram_builder=diagram,
                default_name="AWS Permissions map",
            )
