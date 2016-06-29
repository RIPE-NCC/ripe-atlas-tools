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

from __future__ import print_function, absolute_import

import itertools
import six
import requests
import sys

from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.tools.aggregators import ValueKeyAggregator, aggregate

from .base import Command as BaseCommand, TabularFieldsMixin
from ..exceptions import RipeAtlasToolsException
from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from ..helpers.validators import ArgumentType


# Unknown latitude-longitude coordinates.
UNK_COORDS = -1111.0, -1111.0


class Command(TabularFieldsMixin, BaseCommand):

    NAME = "probe-search"

    DESCRIPTION = (
        "Fetch and print probes fulfilling specified criteria based on "
        "given filters"
    )

    # Column name: (alignment, width)
    COLUMNS = {
        "id": ("<", 5),
        "asn_v4": ("<", 6),
        "asn_v6": ("<", 6),
        "country": ("^", 7),
        "status": ("<", 15),
        "prefix_v4": ("<", 18),
        "prefix_v6": ("<", 18),
        "coordinates": ("<", 19),
        "is_public": ("^", 6),
        "description": ("<", 30),
        "address_v4": ("<", 15),
        "address_v6": ("<", 39),
        "is_anchor": ("^", 6),
    }

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self.aggregators = []
        self.first_line_padding = False

    def add_arguments(self):
        """Adds all commands line arguments for this command."""
        asn = self.parser.add_argument_group("ASN")
        asn.add_argument(
            "--asn",
            type=int,
            help="ASN"
        )
        asn.add_argument(
            "--asnv4",
            type=int,
            help="ASNv4"
        )
        asn.add_argument(
            "--asnv6",
            type=int,
            help="ASNv6"
        )

        prefix = self.parser.add_argument_group("Prefix")
        prefix.add_argument(
            "--prefix",
            type=str,
            help="Prefix"
        )
        prefix.add_argument(
            "--prefixv4",
            type=str,
            help="Prefixv4"
        )
        prefix.add_argument(
            "--prefixv6",
            type=str,
            help="Prefixv6"
        )

        area = self.parser.add_argument_group("Area")
        geo_location = area.add_mutually_exclusive_group()
        geo_location.add_argument(
            "--location",
            type=str,
            help="The location of probes as a string i.e. 'Amsterdam'"
        )
        geo_location.add_argument(
            "--center",
            type=str,
            help="location as <lat>,<lon>-string, i.e. '48.45,9.16'"
        )
        geo_location.add_argument(
            "--country",
            type=str,
            help="The country code of probes."
        )
        area.add_argument(
            "--radius",
            type=int,
            default=15,
            help="Radius in km from specified center/point. Default is 15."
        )

        self.parser.add_argument(
            "--tag",
            type=ArgumentType.tag,
            action="append",
            metavar="TAG",
            help="Include only probes that are marked with these tags. "
                 "Use --tag multiple times to filter on the basis of more "
                 "than one tag. "
                 "Example: --tag system-ipv6-works --tag system-ipv4-works",
            dest="tags"
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            default=25,
            help="Return limited number of probes"
        )
        self.parser.add_argument(
            "--field",
            type=str,
            action="append",
            choices=self.COLUMNS.keys(),
            default=[],
            help="The field(s) to display. Invoke multiple times for multiple "
                 "fields. The default is id, asn_v4, asn_v6, country, and "
                 "status."
        )
        self.parser.add_argument(
            "--aggregate-by",
            type=str,
            choices=[
                'country',
                'asn_v4', 'asn_v6',
                'prefix_v4', 'prefix_v6'
            ],
            action="append",
            help=(
                "Aggregate list of probes based on all specified aggregations."
                " Multiple aggregations supported."
            )
        )
        self.parser.add_argument(
            "--all",
            action='store_true',
            help="Fetch *ALL* probes. That will give you a loooong list."
        )
        self.parser.add_argument(
            "--max-per-aggregation",
            type=int,
            help="Maximum number of probes per aggregated bucket."
        )
        self.parser.add_argument(
            "--ids-only",
            action='store_true',
            help=(
                "Print only IDs of probes. Useful to pipe it to another "
                "command."
            )
        )
        self.parser.add_argument(
            "--status",
            type=int,
            choices=[0, 1, 2, 3],
            help=(
                "Probe's connection status [0 - Never Connected, "
                "1 - Connected, 2 - Disconnected, 3 - Abandoned]"
            )
        )

    def run(self):

        if not self.arguments.field:
            self.arguments.field = (
                "id", "asn_v4", "asn_v6", "country", "status")

        if self.arguments.all:
            self.arguments.limit = sys.maxsize if six.PY3 else sys.maxint

        filters = self.build_request_args()

        if not filters and not self.arguments.all:
            raise RipeAtlasToolsException(colourise(
                "Typically you'd want to run this with some arguments to "
                "filter the probe \nlist, as fetching all of the probes can "
                "take a Very Long Time.  However, if you \ndon't care about "
                "the wait, you can use --all and go get yourself a coffee.",
                "blue"
            ))

        self.set_aggregators()
        probes = ProbeRequest(
            return_objects=True, user_agent=self.user_agent, **filters)
        truncated_probes = itertools.islice(probes, self.arguments.limit)

        if self.arguments.ids_only:
            for probe in truncated_probes:
                print(probe.id)
            return

        hr = self._get_horizontal_rule()

        print(self._get_filter_display(filters))
        print(colourise(self._get_header(), "bold"))
        print(colourise(hr, "bold"))

        if self.arguments.aggregate_by:

            buckets = aggregate(list(truncated_probes), self.aggregators)
            self.render_aggregation(buckets)

        else:

            for probe in truncated_probes:
                print(self._get_line(probe))

        print(colourise(hr, "bold"))

        # Print total count of found measurements
        print(("{:>" + str(len(hr)) + "}\n").format(
            "Showing {} of {} total probes".format(
                min(self.arguments.limit, probes.total_count) or "all",
                probes.total_count
            )
        ))

    def render_aggregation(self, aggregation_data, indent=0):
        """
        Recursively traverses through aggregation data and print them indented.
        """

        if isinstance(aggregation_data, dict):

            for k, v in aggregation_data.items():

                if not indent:
                    if self.first_line_padding:
                        print("")
                    else:
                        self.first_line_padding = True

                print((u" " * indent) + colourise(k, "bold"))
                self.render_aggregation(v, indent=indent + 1)

        elif isinstance(aggregation_data, list):

            for index, probe in enumerate(aggregation_data):
                print(" ", end="")
                print(self._get_line(probe))
                if self.arguments.max_per_aggregation:
                    if index >= self.arguments.max_per_aggregation - 1:
                        break

    def build_request_args(self):
        """
        Builds the request arguments from parser arguments and returns a dict
        that can be used with ATLAS API.
        """
        if self.arguments.all:
            return {}

        return self._clean_request_args()

    def _clean_request_args(self):
        """Cleans all arguments for the API request and checks for sanity."""
        args = {}

        if any(
            [self.arguments.asn, self.arguments.asnv4, self.arguments.asnv6]
        ):
            args.update(self._clean_asn())

        if any([
            self.arguments.prefix,
            self.arguments.prefixv4,
            self.arguments.prefixv6
        ]):
            args.update(self._clean_prefix())

        if self.arguments.location:
            args.update(self._clean_location())

        if self.arguments.center:
            args.update(self._clean_center())

        if self.arguments.country:
            args.update(self._clean_country_code())

        if self.arguments.status is not None:
            args.update({"status": self.arguments.status})

        if self.arguments.tags:
            args.update({"tags": ",".join(self.arguments.tags)})

        return args

    def _clean_asn(self):
        """Make sure ASN arguments don't conflict and make sense."""
        asn = self.arguments.asn
        asnv4 = self.arguments.asnv4
        asnv6 = self.arguments.asnv6

        if asn and (asnv4 or asnv6):
            exc_log = (
                "Specifying argument --asn together with --asnv4/--asnv6 "
                "doesn't make sense"
            )
            raise RipeAtlasToolsException(exc_log)
        if asn:
            return {"asn": asn}

        asn_args = {}
        if asnv4:
            asn_args["asn_v4"] = asnv4

        if asnv6:
            asn_args["asn_v6"] = asnv6

        return asn_args

    def _clean_prefix(self):
        """Make sure ASN arguments don't conflict and make sense."""
        prefix = self.arguments.prefix
        prefixv4 = self.arguments.prefixv4
        prefixv6 = self.arguments.prefixv6

        if prefix and (prefixv4 or prefixv6):
            exc_log = (
                "Specifying argument --prefix together with "
                "--prefixv4/--prefixv6 doesn't make sense"
            )
            raise RipeAtlasToolsException(exc_log)
        if prefix:
            return {"prefix": prefix}

        prefix_args = {}
        if prefixv4:
            prefix_args["prefix_v4"] = prefixv4

        if prefixv6:
            prefix_args["prefix_v6"] = prefixv6

        return prefix_args

    def _clean_location(self):
        """Make sure location argument are sane."""
        lat, lng = self.location2degrees()
        if self.arguments.radius:
            location_args = {
                "radius": "{0},{1}:{2}".format(lat, lng, self.arguments.radius)
            }
        else:
            location_args = {"latitude": lat, "longitude": lng}

        return location_args

    def location2degrees(self):
        """Fetches degrees based on the given location."""
        error_log = (
            "Following error occured while trying to fetch lat/lon"
            "for location <{}>:\n{}"
        )
        goole_api_url = "http://maps.googleapis.com/maps/api/geocode/json"
        try:
            result = requests.get(goole_api_url, params={
                "sensor": "false",
                "address": self.arguments.location
            })
        except (
            requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout,
        ) as e:
            error_log = error_log.format(self.arguments.location, e)
            raise RipeAtlasToolsException(error_log)

        result = result.json()

        try:
            lat = result["results"][0]["geometry"]["location"]["lat"]
            lng = result["results"][0]["geometry"]["location"]["lng"]
        except (KeyError, IndexError) as e:
            error = error_log.format(self.arguments.location, e)
            raise RipeAtlasToolsException(error)

        return str(lat), str(lng)

    def _clean_center(self):
        """Make sure center argument are sane."""
        try:
            lat, lng = self.arguments.center.split(",")
        except ValueError:
            raise RipeAtlasToolsException(
                "Point argument should be in <lat,lng> format."
            )

        if self.arguments.radius:
            center_args = {
                "radius": "{0},{1}:{2}".format(lat, lng, self.arguments.radius)
            }
        else:
            center_args = {"latitude": lat, "longitude": lng}

        return center_args

    def _clean_country_code(self):
        """Make sure country_code argument are sane."""
        return {"country_code": self.arguments.country}

    def set_aggregators(self):
        """
        Builds and returns the key aggregators that will be used in
        the aggregation.
        """

        self.aggregators = []

        if not self.arguments.aggregate_by:
            return

        for key in self.arguments.aggregate_by:
            if key == "country":
                self.aggregators.append(ValueKeyAggregator(
                    key="country_code", prefix="Country"))
            else:
                self.aggregators.append(ValueKeyAggregator(key=key))

    def _get_line_items(self, probe):

        r = []

        for field in self.arguments.field:
            if field == "country":
                r.append((probe.country_code or "").lower())
            elif field in ("asn_v4", "asn_v6"):
                r.append(getattr(probe, field) or "")
            elif field == "description":
                description = sanitise(probe.description) or ""
                r.append(description[:self.COLUMNS["description"][1]])
            elif field == "coordinates":
                if probe.geometry and probe.geometry["coordinates"]:
                    lng, lat = probe.geometry["coordinates"]
                else:
                    lng, lat = UNK_COORDS
                r.append(u"{},{}".format(lat, lng))
            elif field in ("is_public", "is_anchor"):
                if getattr(probe, field):
                    r.append(u"\u2714")  # Check mark
                else:
                    r.append(u"\u2718")  # X
            else:
                r.append(sanitise(getattr(probe, field)))

        return r

    @staticmethod
    def _get_colour_from_status(status):
        if status == "Connected":
            return "green"
        if status == "Disconnected":
            return "yellow"
        if status == "Abandoned":
            return "red"
        return "white"

    def _get_line_format(self):
        r = TabularFieldsMixin._get_line_format(self)
        if not self.aggregators:
            return r
        return (u" " * len(self.aggregators)) + r

    def _get_header_names(self):
        r = []
        for field in self.arguments.field:
            if field == "id":
                r.append("ID")
            elif field == "is_public":
                r.append("Public")
            elif field == "is_anchor":
                r.append("Anchor")
            else:
                r.append(field.capitalize())
        return r

    def _get_line(self, probe):
        """
        Python 2 and 3 differ on how to render strings with non-ascii characters
        in them, so we have to accommodate both here.
        """

        if six.PY2:

            return colourise(
                self._get_line_format().format(
                    *self._get_line_items(probe)
                ).encode("utf-8"),
                self._get_colour_from_status(probe.status)
            )

        return colourise(
            self._get_line_format().format(*self._get_line_items(probe)),
            self._get_colour_from_status(probe.status)
        )

    def _get_filter_key_value_pair(self, k, v):
        if k == "country_code":
            return "Country", v.upper()
        if k == "asn":
            return "ASN", v
        return TabularFieldsMixin._get_filter_key_value_pair(self, k, v)
