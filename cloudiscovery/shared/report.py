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
            # Report to limit
            if resource.limits:
                usage = (
                    str(resource.limits.usage)
                    + " - "
                    + str(resource.limits.percent)
                    + "%"
                )
                # pylint: disable=line-too-long
                message_handler(
                    "service: {} - quota code: {} - quota name: {} - aws default quota: {} - applied quota: {} - usage: {}".format(  # noqa: E501
                        resource.limits.service,
                        resource.limits.quota_code,
                        resource.limits.quota_name,
                        resource.limits.aws_limit,
                        resource.limits.local_limit,
                        usage,
                    ),
                    "OKBLUE",
                )
            elif resource.attributes:
                # pylint: disable=too-many-format-args
                message_handler(
                    "\nservice: {} - type: {} - id: {} - resource name: {}".format(
                        resource.group,
                        resource.digest.type,
                        resource.digest.id,
                        resource.name,
                    ),
                    "OKBLUE",
                )
                for (
                    resource_attr_key,
                    resource_attr_value,
                ) in resource.attributes.items():
                    message_handler(
                        "service: {} - type: {} - name: {} -> {}: {}".format(
                            resource.group,
                            resource.digest.type,
                            resource.name,
                            resource_attr_key,
                            resource_attr_value,
                        ),
                        "OKBLUE",
                    )
            else:
                message_handler(
                    "type: {} - id: {} - name: {} - details: {}".format(
                        resource.digest.type,
                        resource.digest.id,
                        resource.name,
                        resource.details,
                    ),
                    "OKBLUE",
                )

        if resource_relations:
            message_handler("\n\nFound relations", "HEADER")
            for resource_relation in resource_relations:
                message = "type: {} - id: {} -> type: {} - id: {}".format(
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

        group_title = "Group"
        if resources:
            if resources[0].limits:
                html_output = dir_template.get_template("report_limits.html").render(
                    default_name=title, resources_found=resources
                )
            else:
                if resources[0].attributes:
                    group_title = "Service"
                html_output = dir_template.get_template("report_html.html").render(
                    default_name=title,
                    resources_found=resources,
                    resources_relations=resource_relations,
                    diagram_image=diagram_image,
                    group_title=group_title,
                )

            self.make_directories()

            name_output = PATH_REPORT_HTML_OUTPUT + filename + ".html"

            with open(name_output, "w") as file_output:
                file_output.write(html_output)

            message_handler("\n\nHTML report generated", "HEADER")
            message_handler("Check your HTML report: " + name_output, "OKBLUE")
