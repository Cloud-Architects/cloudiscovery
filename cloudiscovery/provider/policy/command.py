from typing import List

from provider.policy.diagram import PolicyDiagram

from shared.common import Filterable, BaseOptions
from shared.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.diagram import NoDiagram


class PolicyOptions(BaseAwsOptions, BaseOptions):
    def __init__(self, verbose, filters, session, region_name):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)


class Policy(BaseAwsCommand):
    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        for region in self.region_names:
            self.init_region_cache(region)
            options = PolicyOptions(
                verbose=verbose,
                filters=filters,
                session=self.session,
                region_name=region,
            )

            command_runner = AwsCommandRunner(filters)
            if diagram:
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
