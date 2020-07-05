from typing import List

from shared.common import Filterable, BaseOptions
from shared.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.diagram import NoDiagram


class AllOptions(BaseAwsOptions, BaseOptions):
    services: List[str]

    # pylint: disable=too-many-arguments
    def __init__(self, verbose, filters, session, region_name, services: List[str]):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)
        self.services = services


class All(BaseAwsCommand):
    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
    ):
        for region in self.region_names:
            self.init_region_cache(region)
            options = AllOptions(
                verbose=verbose,
                filters=filters,
                session=self.session,
                region_name=region,
                services=services,
            )

            command_runner = AwsCommandRunner(filters)
            command_runner.run(
                provider="all",
                options=options,
                diagram_builder=NoDiagram(),
                title="AWS Resources - Region {}".format(region),
                # pylint: disable=no-member
                filename=options.resulting_file_name("all"),
            )
