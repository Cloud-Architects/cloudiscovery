import base64
import os
import os.path
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

from shared.common import Resource, ResourceEdge, message_handler
from shared.diagram import PATH_DIAGRAM_OUTPUT
from shared.error_handler import exception

PATH_REPORT_HTML_OUTPUT = "./assets/html_report/"


class Report(object):
    @staticmethod
    def make_directories():
        Path(PATH_REPORT_HTML_OUTPUT).mkdir(parents=True, exist_ok=True)

    @exception
    def general_report(
        self, resources: List[Resource], resource_relations: List[ResourceEdge]
    ):

        message_handler("\n\nFound resources", "HEADER")

        for resource in resources:
            message = "resource type: {} - resource id: {} - resource name: {} - resource details: {}".format(
                resource.digest.type,
                resource.digest.id,
                resource.name,
                resource.details,
            )

            message_handler(message, "OKBLUE")

        message_handler("\n\nFound relations", "HEADER")
        for resource_relation in resource_relations:
            message = "resource type: {} - resource id: {} -> resource type: {} - resource id: {}".format(
                resource_relation.from_node.type,
                resource_relation.from_node.id,
                resource_relation.to_node.type,
                resource_relation.to_node.id,
            )

            message_handler(message, "OKBLUE")

    @exception
    def html_report(
        self,
        resources: List[Resource],
        resource_relations: List[ResourceEdge],
        title: str,
        filename: str,
    ):
        dir_template = Environment(
            loader=FileSystemLoader(
                os.path.dirname(os.path.abspath(__file__)) + "/../templates/"
            ),
            trim_blocks=True,
        )

        """generate image64 to add to report"""
        diagram_image = None
        if filename is not None:
            image_name = PATH_DIAGRAM_OUTPUT + filename + ".png"
            if os.path.exists(image_name):
                with open(image_name, "rb") as image_file:
                    diagram_image = base64.b64encode(image_file.read()).decode("utf-8")

        html_output = dir_template.get_template("report_html.html").render(
            default_name=title,
            resources_found=resources,
            resources_relations=resource_relations,
            diagram_image=diagram_image,
        )

        self.make_directories()

        name_output = PATH_REPORT_HTML_OUTPUT + filename + ".html"

        with open(name_output, "w") as file_output:
            file_output.write(html_output)

        message_handler("\n\nHTML report generated", "HEADER")
        message_handler("Check your HTML report: " + name_output, "OKBLUE")
