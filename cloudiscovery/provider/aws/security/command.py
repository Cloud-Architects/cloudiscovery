from typing import List

from provider.aws.common_aws import BaseAwsOptions, BaseAwsCommand, AwsCommandRunner
from shared.common import (
    ResourceCache,
    Filterable,
    BaseOptions,
)
from shared.diagram import NoDiagram


class SecurityOptions(BaseAwsOptions, BaseOptions):
    commands: List[str]

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        verbose: bool,
        filters: List[Filterable],
        session,
        region_name,
        commands,
    ):
        BaseAwsOptions.__init__(self, session, region_name)
        BaseOptions.__init__(self, verbose, filters)
        self.commands = commands


class SecurityParameters:
    def __init__(self, session, region: str, commands, options: SecurityOptions):
        self.region = region
        self.cache = ResourceCache()
        self.session = session
        self.options = options
        self.commands = commands


class Security(BaseAwsCommand):
    def __init__(self, region_names, session, commands, partition_code):
        """
        All AWS resources

        :param region_names:
        :param session:
        :param commands:
        :param partition_code:
        """
        super().__init__(region_names, session, partition_code)
        self.commands = commands

    #pylint: disable=too-many-arguments
    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
        import_module: str,
    ):

        for region in self.region_names:
            security_options = SecurityOptions(
                verbose=verbose,
                filters=filters,
                session=self.session,
                region_name=region,
                commands=self.commands,
            )

            command_runner = AwsCommandRunner()
            command_runner.run(
                provider="security",
                options=security_options,
                diagram_builder=NoDiagram(),
                title="AWS Security - Region {}".format(region),
                # pylint: disable=no-member
                filename=security_options.resulting_file_name("security"),
                import_module=import_module,
            )
