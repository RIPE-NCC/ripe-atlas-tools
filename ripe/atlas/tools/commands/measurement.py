from __future__ import print_function, absolute_import

import six
from datetime import datetime

from ripe.atlas.cousteau import Measurement
from ripe.atlas.cousteau.exceptions import APIResponseError

from .base import Command as BaseCommand
from ..exceptions import RipeAtlasToolsException
from ..helpers.colours import colourise


class Command(BaseCommand):

    NAME = "measurement"
    DESCRIPTION = (
        "Returns the meta data for one measurement"
    )

    def add_arguments(self):
        self.parser.add_argument("id", type=int, help="The measurement id")

    def run(self):

        try:
            measurement = Measurement(id=self.arguments.id)
        except APIResponseError:
            raise RipeAtlasToolsException(
                "That measurement does not appear to exist")

        self.render_basic(measurement)
        self.render_ping(measurement)

    @classmethod
    def render_basic(cls, measurement):
        url_template = "https://atlas.ripe.net/measurements/{}/"
        cls._render(measurement, (
            ("id", "ID"),
            ("id", "URL", lambda _: colourise(url_template.format(_), "cyan")),
            ("type", "Type", lambda _: _["name"]),
            ("status", "Status", lambda _: _["name"]),
            ("description", "Description"),
            ("af", "Address Family"),
            ("is_public", "Public?", cls._prettify_boolean),
            ("is_oneoff", "One-off?", cls._prettify_boolean),
            ("destination_name", "Destination Name"),
            ("destination_address", "Destination Address"),
            ("destination_asn", "Destination ASN"),
            ("interval", "Interval"),
            ("spread", "Spread"),
            ("creation_time", "Created", cls._prettify_time),
            ("start_time", "Started", cls._prettify_time),
            ("stop_time", "Stopped", cls._prettify_time),
            ("probes_requested", "Probes Requested"),
            ("probes_scheduled", "Probes Scheduled"),
            ("probes_currently_involved", "Probes Involved"),
            ("participant_count", "Participant Count"),
            ("is_all_scheduled", "Fully Scheduled?", cls._prettify_boolean),
            ("resolved_ips", "Resolved IPs", lambda _: ", ".join(_)),
            ("resolve_on_probe", "Resolve on the Probe", cls._prettify_boolean),
        ))

    @classmethod
    def render_ping(cls, measurement):
        cls._render(measurement, (
            ("packets", "Packets"),
            ("size", "Size")
        ))

    @staticmethod
    def _prettify_time(timestamp):
        return "{} UTC".format(
            datetime.fromtimestamp(timestamp).isoformat().replace("T", " "))

    @staticmethod
    def _prettify_boolean(boolean):

        checkmark = u"\u2714"
        x = u"\u2718"
        if six.PY2:
            checkmark = checkmark.encode("utf-8")
            x = x.encode("utf-8")

        if boolean:
            return colourise(checkmark, "green")
        return colourise(x, "red")

    @staticmethod
    def _render(measurement, keys):
        for prop in keys:
            if prop[0] in measurement.meta_data:
                value = measurement.meta_data[prop[0]]
                if value is None:
                    value = "N/A"
                elif len(prop) == 3:
                    value = prop[2](value)
                print("{}  {}".format(
                    colourise("{:20}".format(prop[1]), "bold"),
                    value
                ))
