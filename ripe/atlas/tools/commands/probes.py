from __future__ import print_function, absolute_import
import sys
import requests

from ripe.atlas.cousteau import ProbeRequest
from ripe.atlas.tools.aggregators import ValueKeyAggregator, aggregate

from ..exceptions import RipeAtlasToolsException
from ..renderers.probes import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "probes"

    DESCRIPTION = (
        "Fetches and prints probes fulfilling specified criteria based on "
        "given filters."
    )

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
            "--country-code",
            type=str,
            help="The country code of probes."
        )
        area.add_argument(
            "--radius",
            type=int,
            help="Radius in km from specified center/point."
        )

        self.parser.add_argument(
            "--limit",
            type=int,
            help="Return limited number of probes"
        )
        self.parser.add_argument(
            "--additional-fields",
            type=str,
            help=(
                "Print additional probe fields. Specify field names as given "
                "from the API as a comma separated string."
            )
        )
        self.parser.add_argument(
            "--aggregate-by",
            type=str,
            choices=[
                'country_code',
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

    def run(self):
        filters = self.build_request_args()
        probes_request = ProbeRequest(return_objects=True, **filters)
        probes = list(probes_request)

        if self.arguments.limit:
            probes = probes[:self.arguments.limit]

        if self.arguments.ids_only:
            ids = self.produce_ids_only(probes)
            sys.stdout.write(ids)
            return

        render_args = self._clean_render_args()
        renderer = Renderer(**render_args)
        renderer.on_start()

        if self.arguments.aggregate_by:

            aggregators = self.get_aggregators()
            buckets = aggregate(probes, aggregators)
            renderer.render_aggregation(buckets)

        else:

            renderer.on_table_title()
            for index, probe in enumerate(probes):
                renderer.on_result(probe)

        renderer.total_count = probes_request.total_count
        renderer.on_finish()

    def produce_ids_only(self, probes):
        """If user has specified ids-only arg print only ids and exit."""
        probe_ids = []
        for index, probe in enumerate(probes):
            probe_ids.append(str(probe.id))
            if self.arguments.limit and index >= self.arguments.limit - 1:
                break

        return ",".join(probe_ids)

    def _clean_render_args(self):
        """
        Clean arguments that will be used by renderer and return the kwargs
        structure for it.
        """
        args = {"max_per_aggr": self.arguments.max_per_aggregation}

        if self.arguments.additional_fields:
            args.update(self._clean_additional_fields())

        return args

    def _clean_additional_fields(self):
        """Parse and store additional fields argument."""
        additional_fields = [
            x.strip() for x in self.arguments.additional_fields.split(",")
        ]

        return {"additional_fields": additional_fields}

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

        set_args = [k for k, v in vars(self.arguments).items() if v]
        if not set_args:
            raise RipeAtlasToolsException(
                "You must specify at least one argument. Try --help for usage.")

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

        if self.arguments.country_code:
            args.update(self._clean_country_code())

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
        country_code_args = {"country_code": self.arguments.country_code}

        return country_code_args

    def get_aggregators(self):
        """
        Builds and returns the key aggregators that will be used in
        the aggregation.
        """
        aggregation_keys = []
        for aggr_key in self.arguments.aggregate_by:
            aggregation_keys.append(ValueKeyAggregator(key=aggr_key))
        return aggregation_keys
