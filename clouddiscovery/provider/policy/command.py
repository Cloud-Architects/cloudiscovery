from provider.policy.diagram import PolicyDiagram
from shared.command import BaseCommand, CommandRunner
from shared.common import BaseAwsOptions
from shared.diagram import NoDiagram


class Policy(BaseCommand):
    def run(self):
        for region in self.region_names:
            options = BaseAwsOptions(session=self.session, region_name=region)

            command_runner = CommandRunner(self.filters)
            if self.diagram:
                diagram = PolicyDiagram()
            else:
                diagram = NoDiagram()
            command_runner.run(
                provider="policy",
                options=options,
                diagram_builder=diagram,
                title="AWS IAM Policies - Region {}".format(region),
                filename=options.resulting_file_name("policy"),
            )
