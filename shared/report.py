from shared.common import *
from shared.error_handler import exception


class Report(object):

    def __init__(self, resources):
        self.resources = resources

    @exception
    def generalReport(self):

        message_handler("\n\nRESOURCES FOUND", "HEADER")

        for alldata in self.resources:
            """ In case of some resource check failure, response may be None"""
            if isinstance(alldata, list):
                for rundata in alldata:
                    message = "resource type: {} -> resource id: {} -> resource name: {} -> resource details: {}" \
                        .format(rundata.type, rundata.id, rundata.name, rundata.details)

                    message_handler(message, "OKBLUE")
