# Copyright (c) 2016 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ripe.atlas.cousteau import Measurement
from ripe.atlas.cousteau.exceptions import APIResponseError

from .base import Command as BaseCommand, MetaDataMixin
from ..exceptions import RipeAtlasToolsException
from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from ..helpers.validators import ArgumentType
from ..settings import conf


class Command(MetaDataMixin, BaseCommand):

    NAME = "measurement-info"
    DESCRIPTION = "Return the meta data for one measurement"

    def add_arguments(self):
        self.parser.add_argument(
            "id", type=ArgumentType.msm_id_or_name(), help="The measurement id or alias"
        )

    def run(self):

        try:
            measurement = Measurement(
                server=conf["api-server"],
                id=self.arguments.id,
                user_agent=self.user_agent,
            )
        except APIResponseError:
            raise RipeAtlasToolsException("That measurement does not appear to exist")

        self.render_basic(measurement)
        getattr(self, "render_{}".format(measurement.type.lower()))(measurement)

    @classmethod
    def render_basic(cls, measurement):
        cls._render(
            measurement,
            (
                ("id", "ID"),
                (
                    "id",
                    "URL",
                    lambda id: colourise(
                        f"{conf['website-url']}/measurements/id/", "cyan"
                    ),
                ),
                ("type", "Type", cls._prettify_type),
                ("status", "Status"),
                ("description", "Description", sanitise),
                ("af", "Address Family"),
                ("is_public", "Public?", cls._prettify_boolean),
                ("is_oneoff", "One-off?", cls._prettify_boolean),
                ("target", "Target Name", sanitise),
                ("target_address", "Target Address", sanitise),
                ("target_asn", "Target ASN"),
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
            ),
        )

    @classmethod
    def render_ping(cls, measurement):
        cls._render(
            measurement,
            (
                ("packets", "Packets"),
                ("size", "Size"),
            ),
        )

    @classmethod
    def render_traceroute(cls, measurement):
        cls._render(
            measurement,
            (
                ("packets", "Packets"),
                ("protocol", "Protocol"),
                ("dont_fragment", "Don't Fragment", cls._prettify_boolean),
                ("paris", "Paris"),
                ("first_hop", "First Hop"),
                ("max_hops", "Maximum Hops"),
                ("timeout", "Timeout"),
                ("size", "Size"),
                ("destination_option_size", "Destination Option Size"),
                ("hop_by_hop_option_size", "Hop-by-hop Option Size"),
                ("gap_limit", "Gap Limit"),
            ),
        )

    @classmethod
    def render_dns(cls, measurement):
        cls._render(
            measurement,
            (
                ("query", "Query", cls._prettify_query),
                ("retry", "Retry Times"),
                ("include_qbuf", "Include the Qbuf?", cls._prettify_boolean),
                ("include_abuf", "Include the Abuf?", cls._prettify_boolean),
                ("protocol", "Protocol"),
                ("prepend_probe_id", "Prepend the Probe ID?"),
                ("udp_payload_size", "UDP Payload Size"),
                (
                    "use_probe_resolver",
                    "Use the Probe's Resolver?",
                    cls._prettify_boolean,
                ),
                ("set_do_bit", "Set the DO Bit?", cls._prettify_boolean),
                ("set_nsid_bit", "Set the NSID Bit?", cls._prettify_boolean),
                ("set_rd_bit", "Set the RD Bit?", cls._prettify_boolean),
                ("set_cd_bit", "Set the CD Bit?", cls._prettify_boolean),
            ),
        )

    @classmethod
    def render_sslcert(cls, measurement):
        cls._render(measurement, (("port", "Port"),))

    @classmethod
    def render_http(cls, measurement):

        cls._render(
            measurement,
            (
                ("header_bytes", "Header Bytes"),
                ("version", "Version"),
                ("method", "Method"),
                ("port", "Port"),
                ("path", "Path", sanitise),
                ("query_string", "Query String", sanitise),
                ("user_agent", "User-Agent"),
                ("max_bytes_read", "Body Bytes"),
            ),
        )

        timing_verbosity = 0
        if "extended_timing" in measurement.meta_data:
            if measurement.meta_data["extended_timing"]:
                timing_verbosity = 1
                if "more_extended_timing" in measurement.meta_data:
                    if measurement.meta_data["more_extended_timing"]:
                        timing_verbosity = 2
        cls._render_line("Timing Verbosity", timing_verbosity)

    @classmethod
    def render_ntp(cls, measurement):
        cls._render(
            measurement,
            (
                ("packets", "Packets"),
                ("timeout", "Timeout"),
            ),
        )

    @staticmethod
    def _prettify_type(kind):
        types = {
            "ping": "Ping",
            "traceroute": "Traceroute",
            "dns": "DNS",
            "sslcert": "SSL Certificate",
            "http": "HTTP",
            "ntp": "NTP",
        }
        if kind in types:
            return colourise(colourise(types[kind], "bold"), "blue")
        return colourise("Unknown", "red")

    @staticmethod
    def _prettify_query(query):
        return sanitise(
            "{} {} {}".format(query["class"], query["type"], query["value"])
        )

    @classmethod
    def _render(cls, measurement, keys):
        for prop in keys:

            value = cls._get_measurement_property(measurement, prop[0])

            if value != "-" and len(prop) == 3:
                value = prop[2](value)

            cls._render_line(prop[1], value)

    @classmethod
    def _get_measurement_property(cls, measurement, property_name):
        value = getattr(measurement, property_name, None)

        if value is None and property_name in measurement.meta_data:
            value = measurement.meta_data[property_name]

        if value is None:
            value = "-"

        return value
