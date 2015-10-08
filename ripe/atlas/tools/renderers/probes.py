import sys
from .base import Renderer as BaseRenderer
#  from ..helpers.colours import Colour


class Renderer(BaseRenderer):

    RENDERS = []

    def __init__(self, fields=[], additional_fields=[], max_per_aggr=None):
        self.blob = ""
        self.additional_fields = additional_fields
        self.probe_template = ""
        self.header_message = ""
        self.fields = []
        self.max_per_aggr = max_per_aggr
        self.custom_format_flag = False

        if fields:
            self.custom_format_flag = True
            self.fields = fields

        self._construct_probe_line()
        self._construct_header()

        self.fields.extend(self.additional_fields)

    def _construct_header(self):
        """Construct the header message string template"""
        header_fields = []
        header_template = ""

        if not self.custom_format_flag:
            header_fields = ["ID", "ASNv4", "ASNv6", "CC", "Status"]
            header_template = "{:<5}|{:<6}|{:<6}|{:<2}|{:<10}|"
        else:
            for field in self.fields:
                header_fields.append(field.upper())
                header_template += "{:<}|"

        for field in self.additional_fields:
            header_template += "{:<}|"
            header_fields.append(field)

        self.header_message = header_template.format(*header_fields)

    def _construct_probe_line(self):
        """Construct the probe line string template"""
        # special case for ids-only arg
        if self.fields == ["id"]:
            self.probe_template = "{:<}"
            return

        if not self.custom_format_flag:
            self.fields = ["id", "asn_v4", "asn_v6", "country_code", "status"]
            self.probe_template = "{:<5}|{:<6}|{:<6}|{:^2}|{:<}|"
        else:
            for field in self.fields:
                self.probe_template += "{:<}|"

        for fields in self.additional_fields:
            self.probe_template += "{:<}|"

    def render_aggregation(self, aggregation_data, indent=""):
        """Traverses through aggregation data and print them indented"""

        if isinstance(aggregation_data, dict):

            for k, v in aggregation_data.items():
                self.on_aggregation_title(str(k), indent)
                self.render_aggregation(v, indent=indent + " ")

        elif isinstance(aggregation_data, list):

            self.on_table_title(indent + " ")
            for index, data in enumerate(aggregation_data):
                self.on_result(data, indent=indent + " ")

                if self.max_per_aggr and index >= self.max_per_aggr - 1:
                    break

    def on_start(self, indent=""):
        self.blob += "We have found the following probes with the given criteria:\n"

    def on_table_title(self, indent=""):
        """Renders the header of the table"""
        self.blob += "{0}{1}\n".format(indent, self.header_message)

    def on_aggregation_title(self, bucket, indent=""):
        self.blob += "{0}\n".format(indent + bucket)

    def on_result(self, result, probes=None, indent=""):
        fields = []

        for field in self.fields:
            fields.append(getattr(result, field, "Undefined"))

        message = self.probe_template.format(*fields)
        self.blob += "{0}{1}\n".format(indent, message)

    def on_finish(self, total_count):
        self.blob += "Total probes found: {0}\n".format(total_count)
        sys.stdout.write(self.blob)
