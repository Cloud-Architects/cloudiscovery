from provider.iot.command import IotOptions
from shared.common import *
from shared.error_handler import exception


class CERTIFICATE(ResourceProvider):

    def __init__(self, iot_options: IotOptions):
        super().__init__()
        self.iot_options = iot_options

    @exception
    def get_resources(self) -> List[Resource]:

        client = self.iot_options.client('iot')

        resources_found = []

        message_handler("Collecting data from IoT Certificates...", "HEADER")

        for thing in self.iot_options.thing_name['things']:

            response = client.list_thing_principals(thingName=thing['thingName'])

            for data in response['principals']:
            
                if "cert/" in data:

                    lst_cert = data.split("/")

                    data_cert = response = client.describe_certificate(certificateId=lst_cert[1])
                    
                    iot_cert_digest = ResourceDigest(id=data_cert['certificateDescription']['certificateId'],
                                                    type='aws_iot_certificate')
                    resources_found.append(Resource(
                        digest=iot_cert_digest,
                        name=data_cert['certificateDescription']['certificateId'],
                        details='',
                        group='iot'))

                    self.relations_found.append(ResourceEdge(from_node=iot_cert_digest,
                                                            to_node=ResourceDigest(id=thing['thingName'],
                                                                                    type='aws_iot_thing')))

        return resources_found