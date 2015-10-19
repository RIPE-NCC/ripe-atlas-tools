import sys
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = []

    def __init__(self, fields=None, additional_fields=None, max_per_aggr=None):

        self.blob = ""
        self.additional_fields = additional_fields or []
        self.probe_template = ""
        self.header_message = ""
        self.fields = []
        self.max_per_aggr = max_per_aggr
        self.custom_format_flag = False
        self.total_count = 0

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
            header_template = "{:<5} {:<6} {:<6} {:<2} {:<12}"
        else:
            for field in self.fields:
                header_fields.append(field.upper())
                header_template += " {:<}"

        for field in self.additional_fields:
            header_template += " {:<}"
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
            self.probe_template = "{:<5} {:<6} {:<6} {:^2} {:<12}"
        else:
            for field in self.fields:
                self.probe_template += " {:<}"

        for fields in self.additional_fields:
            self.probe_template += " {:<}"

    def render_aggregation(self, aggregation_data, indent=""):
        """
        Recursively traverses through aggregation data and print them indented.
        """

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

    def on_table_title(self, indent=""):
        """Renders the header of the table"""
        self.blob += "{}{}\n".format(indent, self.header_message)

    def on_aggregation_title(self, bucket, indent=""):
        """Renders the title of each aggregation bucket."""
        self.blob += "{}\n".format(indent + bucket)

    def on_result(self, result, indent=""):
        fields = []

        for field in self.fields:
            fields.append(getattr(result, field, ""))

        message = self.probe_template.format(*fields)
        self.blob += "{}{}\n".format(indent, message)
