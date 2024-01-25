# Copyright (c) 2023 RIPE NCC
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

import itertools
import sys
from typing import Any, Dict, List, Mapping, Tuple

import requests
from ripe.atlas.cousteau import ProbeRequest

from ..exceptions import RipeAtlasToolsException
from ..helpers import tabular
from ..helpers.sanitisers import sanitise
from ..helpers.validators import ArgumentType
from ..settings import conf
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "probe-search"
    MAX_PAGE_SIZE = 500  # Request chunks of this size or smaller

    DESCRIPTION = (
        "Fetch and print probes fulfilling specified criteria based on " "given filters"
    )

    COLUMNS: Dict[str, tabular.ColumnDef] = {
        "id": {"align": ">", "width": 7},
        "asn_v4": {"align": ">", "width": 6},
        "asn_v6": {"align": ">", "width": 6},
        "country": {"align": "^", "width": 7},
        "status": {"align": "^", "width": 15},
        "prefix_v4": {"align": ">", "width": 18},
        "prefix_v6": {"align": ">", "width": 18},
        "coordinates": {"align": "^", "width": 19},
        "is_public": {"align": "^", "width": 9},
        "description": {"align": "^", "width": 30},
        "address_v4": {"align": ">", "width": 15},
        "address_v6": {"align": ">", "width": 39},
        "is_anchor": {"align": "^", "width": 9},
    }

    def add_arguments(self) -> None:
        """Adds all commands line arguments for this command."""
        asn = self.parser.add_argument_group("ASN")
        asn.add_argument(
            "--asn",
            type=int,
            help="Probes in IPv4 or IPv6 prefixes announced by this ASN",
        )
        asn.add_argument(
            "--asnv4", type=int, help="Probes in IPv4 prexfixes announced by this ASN"
        )
        asn.add_argument(
            "--asnv6", type=int, help="Probes in IPv6 prefixes announced by this ASN"
        )

        prefix = self.parser.add_argument_group("Prefix")
        prefix.add_argument(
            "--prefix",
            type=str,
            help="Probes with addresses in this IPv4 or IPv6 CIDR prefix",
        )
        prefix.add_argument(
            "--prefixv4", type=str, help="Probes with addresses in this IPv4 prefix"
        )
        prefix.add_argument(
            "--prefixv6", type=str, help="Probes with addresses in this IPv6 prefix"
        )

        area = self.parser.add_argument_group("Area")
        geo_location = area.add_mutually_exclusive_group()
        geo_location.add_argument(
            "--location",
            type=str,
            help="The location of probes as a string i.e. 'Amsterdam'",
        )
        geo_location.add_argument(
            "--center",
            type=str,
            help="Location as <lat>,<lon>-string, i.e. '48.45,9.16'. "
            "Note: use --center=-5,10 (no space) to allow for negative latitudes",
        )
        geo_location.add_argument(
            "--country", type=str, help="The country code of probes."
        )
        area.add_argument(
            "--radius",
            type=int,
            default=15,
            help="Radius in km from specified center/point. Default: 15",
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
            dest="tags",
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            default=25,
            help="Return at most this number of probes. Default: 25",
        )
        self.parser.add_argument(
            "--all",
            action="store_true",
            help="Fetch all probes; takes a long time!",
        )
        self.parser.add_argument(
            "--status",
            type=int,
            choices=[0, 1, 2, 3],
            help=(
                "Probe's connection status [0 - Never Connected, "
                "1 - Connected, 2 - Disconnected, 3 - Abandoned]"
            ),
        )
        self.parser.add_argument(
            "--auth",
            type=str,
            default=conf["authorisation"]["google_geocoding"],
            help=(
                "Google Geocoding API key to be " "used to perform --location search."
            ),
        )
        tabular.add_argument_group(self.parser, self.COLUMNS.keys())

    def run(self) -> None:
        if not self.arguments.field:
            self.arguments.field = [
                "id",
                "asn_v4",
                "asn_v6",
                "country",
                "status",
            ]

        if self.arguments.all:
            self.arguments.limit = sys.maxsize

        filters = self._get_filters()
        request_fields = self._get_request_fields()

        probes = ProbeRequest(
            server=conf["api-server"],
            return_objects=True,
            user_agent=self.user_agent,
            fields=",".join(request_fields),
            page_size=min(self.MAX_PAGE_SIZE, self.arguments.limit),
            **filters
        )
        truncated_probes = itertools.islice(probes, self.arguments.limit)

        renderer = tabular.renderers[self.arguments.format]

        rows = [self._get_row(m) for m in truncated_probes]

        for line in renderer(
            rows=rows,
            total_count=probes.total_count,
            columns=dict((c, self.COLUMNS[c]) for c in self.arguments.field),
            filters=filters,
            arguments=self.arguments,
        ):
            print(line)

    def _get_filters(self) -> Dict[str, str]:
        """
        Get the request filters for sending to the API.
        """
        if self.arguments.all:
            return {}

        args: Dict[str, Any] = {}

        if any([self.arguments.asn, self.arguments.asnv4, self.arguments.asnv6]):
            args.update(self._clean_asn())

        if any(
            [
                self.arguments.prefix,
                self.arguments.prefixv4,
                self.arguments.prefixv6,
            ]
        ):
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

    def _clean_asn(self) -> Mapping[str, int]:
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

    def _clean_prefix(self) -> Dict[str, str]:
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

    def _clean_location(self) -> Dict[str, Any]:
        """Make sure location argument are sane."""
        if not self.arguments.auth:
            raise RipeAtlasToolsException(
                "--location requires a Google Geocoding API  key specified with "
                "--auth or configure command (authorisation.google_geocoding)"
            )
        lat, lng = self.location2degrees()
        if self.arguments.radius:
            location_args = {
                "radius": "{0},{1}:{2}".format(lat, lng, self.arguments.radius)
            }
        else:
            location_args = {"latitude": lat, "longitude": lng}

        return location_args

    def location2degrees(self) -> Tuple[str, str]:
        """Fetches degrees based on the given location."""
        error_log = (
            "The following error occured while trying to fetch lat/lon "
            "for location <{}>:\n\n{}"
        )
        google_api_url = "https://maps.googleapis.com/maps/api/geocode/json"
        try:
            result = requests.get(
                google_api_url,
                params={
                    "key": self.arguments.auth,
                    "address": self.arguments.location,
                },
            )
        except (
            requests.ConnectionError,
            requests.HTTPError,
            requests.Timeout,
        ) as e:
            error_log = error_log.format(self.arguments.location, e)
            raise RipeAtlasToolsException(error_log)

        data = result.json()

        if "error_message" in data:
            error = error_log.format(self.arguments.location, data["error_message"])
            raise RipeAtlasToolsException(error)

        try:
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lng = data["results"][0]["geometry"]["location"]["lng"]
        except (KeyError, IndexError) as e:
            error = error_log.format(self.arguments.location, e)
            raise RipeAtlasToolsException(error)

        return str(lat), str(lng)

    def _clean_center(self) -> Dict[str, Any]:
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

    def _clean_country_code(self) -> Dict[str, str]:
        """Make sure country_code argument are sane."""
        return {"country_code": self.arguments.country}

    def _get_row(self, probe) -> tabular.RowDef:
        r = {}

        for field in self.arguments.field + self.arguments.aggregate_by:
            if field == "country":
                r[field] = (probe.country_code or "").lower()
            elif field in ("asn_v4", "asn_v6"):
                r[field] = getattr(probe, field) or None
            elif field == "description":
                description = sanitise(probe.description) or None
                r[field] = description
            elif field == "coordinates":
                if probe.geometry and probe.geometry["coordinates"]:
                    lng, lat = probe.geometry["coordinates"]
                    r[field] = "{:7.4f} {:8.4f}".format(lat, lng)
                else:
                    r[field] = None
            elif field in ("is_public", "is_anchor"):
                if getattr(probe, field):
                    r[field] = "\u2714"  # Check mark
                else:
                    r[field] = "\u2718"  # X
            else:
                r[field] = sanitise(getattr(probe, field))

        return {"values": r, "colour": self._get_colour_from_status(probe.status)}

    @staticmethod
    def _get_colour_from_status(status: str) -> str:
        if status == "Connected":
            return "green"
        if status == "Disconnected":
            return "yellow"
        if status == "Abandoned":
            return "red"
        return "white"

    def _get_request_fields(self) -> List[str]:
        request_fields = list(self.arguments.field)
        for field in self.arguments.aggregate_by:
            if field not in request_fields:
                request_fields.append(field)
        if "country" in request_fields:
            request_fields.remove("country")
            request_fields.append("country_code")
        if "status" not in request_fields:
            request_fields.append("status")
        if "coordinates" in request_fields:
            request_fields.remove("coordinates")
            request_fields.append("geometry")
        return request_fields
