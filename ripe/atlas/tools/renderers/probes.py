from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = []

    # Column name: (alignment, width)
    COLUMNS = {
        "id": ("<", 5),
        "asn_v4": ("<", 6),
        "asn_v6": ("<", 6),
        "country_code": ("^", 7),
        "status": ("<", 12),
        "prefix_v4": ("<", 18),
        "prefix_v6": ("<", 18),
        "coordinates": ("<", 21),
        "is_public": ("<", 1),
        "description": ("<", ),
        "address_v4": ("<", 15),
        "address_v6": ("<", 39),
        "is_anchor": ("<", 1),
    }

    def __init__(self, fields=None, max_per_aggr=None):

        self.blob = ""
        self.probe_template = ""
        self.header_message = ""
        self.fields = fields
        self.max_per_aggr = max_per_aggr
        self.total_count = 0

        self._construct_probe_line()
        self._construct_header()

    def _get_line_format(self):
        """
        Loop over the field arguments and generate a string that makes use of
        Python's string format mini language.  We later use this string to
        format the values for each row.
        """
        r = ""
        for field in self.fields:
            if r:
                r += " "
            r += ("{:" + "{}{}".format(*self.COLUMNS[field]) + "}")
        return r

    def _get_header(self):
        """
        Generates a header by using the line formatter and the list of field
        arguments.
        """
        return self._get_line_format().format(
            *[_.capitalize() for _ in self.fields]
        )

    def _construct_header(self):
        """Construct the header message string template"""
        header_fields = []
        header_template = ""

        for field in self.fields:
            header_fields.append(field.upper())
            header_template += " {:<}"

        self.header_message = header_template.format(*header_fields)

    def _construct_probe_line(self):
        """Construct the probe line string template"""
        # special case for ids-only arg
        if self.fields == ["id"]:
            self.probe_template = "{:<}"
            return

        for field in self.fields:
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
