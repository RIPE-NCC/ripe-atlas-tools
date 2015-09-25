from __future__ import print_function, absolute_import
import requests
import sys

from ripe.atlas.cousteau import ProbeRequest

from ..exceptions import RipeAtlasToolsException
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "findprobe"

    DESCRIPTION = "Find probes fullfiling specific criteria based on given filters."

    def add_arguments(self):
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
        asn.add_argument(
            "--max-per-as",
            type=int,
            help="Maximum number of probes per ASN"
        )
        prefix = self.parser.add_argument_group("Preifx")
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
            help="The location"
        )
        geo_location.add_argument(
            "--point",
            type=str,
            help="location as <lat>,<lon>-string, ie '48.45,9.16'"
        )
        geo_location.add_argument(
            "--country-code",
            type=str,
            help="The country code"
        )
        area.add_argument(
            "--radius",
            type=int,
            help="Radius"
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            help="Limit"
        )
        self.parser.add_argument(
            "--fields",
            type=str,
            help="Additional fields"
        )
        self.parser.add_argument(
            "--all",
            action='store_true',
            help="Fetch *ALL* probes. That will give you a loooong list."
        )

    def run(self):
        header = False
        filters = self.build_request_args()

        print(self.arguments)
        print(filters)
        probes = ProbeRequest(**filters)
        for probe in probes:
            if not header:
                message = "{0:<5}|{1:<6}|{2:<6}|{3:<2}|{4:<10}".format("ID", "ASNv4", "ASNv6", "CC", "Status")
                sys.stdout.write("{0}\n".format(message))
                header = True
            message = "{0:<5}|{1:<6}|{2:<6}|{3:^2}|{4:<}".format(probe["id"], probe["asn_v4"], probe["asn_v6"], probe["country_code"], probe["status_name"])
            sys.stdout.write("{0}\n".format(message))

    def build_request_args(self):
        """
        Builds the request arguments from parser arguments and returns a dict
        that can be used with ATLAS API.
        """
        if self.arguments.all:
            return {}

        return self._clean()

    def _clean(self):
        """Cleans all arguments and checks for sanity."""
        args = {}

        set_args = [k for k, v in vars(self.arguments).items() if v]
        if not set_args:
            error_msg = "You should specify at least one argument. Try -h option for usuage."
            raise RipeAtlasToolsException(error_msg)

        if any([self.arguments.asn, self.arguments.asnv4, self.arguments.asnv6]):
            args.update(self._clean_asn())

        if any([self.arguments.prefix, self.arguments.prefixv4, self.arguments.prefixv6]):
            args.update(self._clean_prefix())

        if self.arguments.location:
            args.update(self._clean_location())

        if self.arguments.point:
            args.update(self._clean_point())

        if self.arguments.country_code:
            args.update(self._clean_country_code())

        return args

    def _clean_asn(self):
        """Make sure ASN arguments don't conflict and make sense."""
        asn = self.arguments.asn
        asnv4 = self.arguments.asnv4
        asnv6 = self.arguments.asnv6

        if asn and (asnv4 or asnv6):
            raise RipeAtlasToolsException(
                "Specifying argument --asn together with --asnv4/--asnv6 doesn't make sense"
            )
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
            raise RipeAtlasToolsException(
                "Specifying argument --prefix together with --prefixv4/--prefixv6 doesn't make sense"
            )
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
            location_args = {"center": "{0},{1}".format(lat, lng), "distance": self.arguments.radius}
        else:
            location_args = {"latitude": lat, "longitude": lng}

        return location_args

    def location2degrees(self):
        """Fetches degrees based on the given location."""
        error_log = (
            "Following error occured while trying to fetch lat/lon"
            "for location <{0}>:\n{1}"
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
            print(e)
            error = error_log.format(self.arguments.location, e)
            raise RipeAtlasToolsException(error)

        return lat, lng

    def _clean_point(self):
        """Make sure point argument are sane."""
        try:
            lat, lng = self.arguments.point.split(",")
        except ValueError:
            raise RipeAtlasToolsException("Point argument should be in <lat,lng> format.")

        if self.arguments.radius:
            point_args = {"center": "{0},{1}".format(lat, lng), "distance": self.arguments.radius}
        else:
            point_args = {"latitude": lat, "longitude": lng}

        return point_args

    def _clean_country_code(self):
        """Make sure country_code argument are sane."""
        country_code_args = {"country_code": self.arguments.country_code}

        return country_code_args
