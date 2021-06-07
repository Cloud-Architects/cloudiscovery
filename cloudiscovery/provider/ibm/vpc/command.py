from typing import List

from ipaddress import ip_network

from provider.ibm.common_ibm import BaseIbmOptions, BaseIbmCommand, IbmCommandRunner
from provider.ibm.vpc.diagram import VpcDiagram
from shared.common import (
    ResourceDigest,
    VPCE_REGEX,
    SOURCE_IP_ADDRESS_REGEX,
    Filterable,
    BaseOptions,
)
from shared.diagram import NoDiagram, BaseDiagram
from ibm_vpc import VpcV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class VpcOptions(BaseIbmOptions, BaseOptions):
    vpc_id: str

    # pylint: disable=too-many-arguments
    def __init__(
        self, verbose: bool, filters: List[Filterable], apikey, region, vpc_id
    ):
        BaseIbmOptions.__init__(self, apikey, region)
        BaseOptions.__init__(self, verbose, filters)
        self.vpc_id = vpc_id

    def vpc_digest(self):
        return ResourceDigest(id=self.vpc_id, type="ibm_vpc")

    def resulting_file_name(self):
        return "{}_{}".format(self.vpc_id, self.region)


class Vpc(BaseIbmCommand):
    vpc_id: str
    region: str
    apikey: str
    service: VpcV1

    # pylint: disable=too-many-arguments
    def __init__(self, region, apikey, vpc_id, url):
        """
        VPC command

        :param vpc_id:
        :param region:
        :param apikey:
        """
        super().__init__(region, apikey, url)
        self.vpc_id = vpc_id
        self.apikey = apikey
        self.region = region
        authenticator = IAMAuthenticator(self.apikey)
        self.service = VpcV1(authenticator=authenticator)
        vpc_url = url
        self.service.set_service_url(vpc_url)

    def check_vpc(self, service: VpcV1):
        response = self.service.get_vpc(self.vpc_id)

        message = "------------------------------------------------------\n"
        message = message + "VPC: {} - {}\nName: {}".format(
            self.vpc_id,
            self.region,
            response["name"],
        )
        print(message)

    #pylint: disable=too-many-arguments
    def run(
        self,
        diagram: bool,
        verbose: bool,
        services: List[str],
        filters: List[Filterable],
        import_module: str,
    ):
        command_runner = IbmCommandRunner(filters)

        # if vpc is none, get all vpcs and check
        if self.vpc_id is None:
            vpcs = self.service.list_vpcs().get_result()["vpcs"]
            for data in vpcs["Vpcs"]:
                vpc_id = data["id"]
                vpc_options = VpcOptions(
                    verbose=verbose,
                    filters=filters,
                    apikey=self.apikey,
                    region=self.region,
                    vpc_id=vpc_id,
                )
                self.check_vpc(vpc_options)
                diagram_builder: BaseDiagram
                if diagram:
                    diagram_builder = VpcDiagram(vpc_id=vpc_id)
                else:
                    diagram_builder = NoDiagram()
                command_runner.run(
                    provider="vpc",
                    options=vpc_options,
                    diagram_builder=diagram_builder,
                    title="IBM VPC {} Resources - Region {}".format(
                        vpc_id, self.region
                    ),
                    filename=vpc_options.resulting_file_name(),
                    import_module=import_module,
                )
        else:
            vpc_options = VpcOptions(
                verbose=verbose,
                filters=filters,
                apikey=self.apikey,
                region=self.region,
                vpc_id=self.vpc_id,
            )

            # self.check_vpc(vpc_options)
            if diagram:
                diagram_builder = VpcDiagram(vpc_id=self.vpc_id)
            else:
                diagram_builder = NoDiagram()
            command_runner.run(
                provider="vpc",
                options=vpc_options,
                diagram_builder=diagram_builder,
                title="IBM VPC {} Resources - Region {}".format(
                    self.vpc_id, self.region
                ),
                filename=vpc_options.resulting_file_name(),
                import_module=import_module,
            )


# pylint: disable=too-many-branches
def check_ipvpc_inpolicy(document, vpc_options: VpcOptions):
    document = document.replace("\\", "").lower()

    # Checking if VPC is inside document, it's a 100% true information
    # pylint: disable=no-else-return
    if vpc_options.vpc_id in document:
        return "direct VPC reference"
    else:
        # Vpc_id not found, trying to discover if it's a potencial subnet IP or VPCE is allowed
        if "ibm:sourcevpce" in document:

            # Get VPCE found
            ibm_sourcevpces = []
            for vpce_tuple in VPCE_REGEX.findall(document):
                ibm_sourcevpces.append(vpce_tuple[1])

            # Get all VPCE of this VPC
            ec2 = vpc_options.client("ec2")

            filters = [{"Name": "vpc-id", "Values": [vpc_options.vpc_id]}]

            vpc_endpoints = ec2.describe_vpc_endpoints(Filters=filters)

            # iterate VPCEs found found
            if len(vpc_endpoints["VpcEndpoints"]) > 0:
                matching_vpces = []
                # Iterate VPCE to match vpce in Policy Document
                for data in vpc_endpoints["VpcEndpoints"]:
                    if data["VpcEndpointId"] in ibm_sourcevpces:
                        matching_vpces.append(data["VpcEndpointId"])
                return "VPC Endpoint(s): " + (", ".join(matching_vpces))

        if "ibm:sourceip" in document:

            # Get ip found
            ibm_sourceips = []
            for vpce_tuple in SOURCE_IP_ADDRESS_REGEX.findall(document):
                ibm_sourceips.append(vpce_tuple[1])
            # Get subnets cidr block
            ec2 = vpc_options.client("ec2")

            filters = [{"Name": "vpc-id", "Values": [vpc_options.vpc_id]}]

            subnets = ec2.describe_subnets(Filters=filters)
            overlapping_subnets = []
            # iterate ips found
            for ipfound in ibm_sourceips:

                # Iterate subnets to match ipaddress
                for subnet in list(subnets["Subnets"]):
                    ipfound = ip_network(ipfound)
                    network_addres = ip_network(subnet["CidrBlock"])

                    if ipfound.overlaps(network_addres):
                        overlapping_subnets.append(
                            "{} ({})".format(str(network_addres), subnet["SubnetId"])
                        )
            if len(overlapping_subnets) != 0:
                return "source IP(s): {} -> subnet CIDR(s): {}".format(
                    ", ".join(ibm_sourceips), ", ".join(overlapping_subnets)
                )

        return False
