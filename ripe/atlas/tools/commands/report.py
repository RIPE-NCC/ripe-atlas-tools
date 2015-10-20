from __future__ import print_function

from ripe.atlas.cousteau import AtlasRequest, Measurement, APIResponseError

from ..aggregators import RangeKeyAggregator, ValueKeyAggregator, aggregate
from ..exceptions import RipeAtlasToolsException
from ..helpers.rendering import SaganSet, Rendering
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = "Report the results of a measurement.\n\nExample:\n" \
                  "  ripe-atlas report 1001 --probes 157,10006\n"
    URLS = {
        "latest": "/api/v2/measurements/{}/latest.json",
    }
    AGGREGATORS = {
        "country": ["probe.country_code", ValueKeyAggregator],
        "rtt-median": [
            "rtt_median",
            RangeKeyAggregator,
            [10, 20, 30, 40, 50, 100, 200, 300]
        ],
        "status": ["probe.status", ValueKeyAggregator],
        "asn_v4": ["probe.asn_v4", ValueKeyAggregator],
        "asn_v6": ["probe.asn_v6", ValueKeyAggregator],
        "prefix_v4": ["probe.prefix_v4", ValueKeyAggregator],
        "prefix_v6": ["probe.prefix_v6", ValueKeyAggregator],
    }

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want reported"
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers,
            help="A comma-separated list of probe ids you want to see "
                 "exclusively."
        )
        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )
        self.parser.add_argument(
            "--aggregate-by",
            type=str,
            choices=self.AGGREGATORS.keys(),
            action="append",
            help="Tell the rendering engine to aggregate the results by the "
                 "selected option.  Note that if you opt for aggregation, no "
                 "output will be generated until all results are received."
        )

    def run(self):

        try:
            measurement = Measurement(id=self.arguments.measurement_id)
        except APIResponseError:
            raise RipeAtlasToolsException("That measurement does not exist")

        latest_url = self.URLS["latest"].format(measurement.id)
        if self.arguments.probes:
            latest_url += "?probes={}".format(self.arguments.probes)

        renderer = Renderer.get_renderer(
            self.arguments.renderer, measurement.type.lower())()

        results = AtlasRequest(url_path=latest_url).get()[1]

        if not results:
            raise RipeAtlasToolsException(
                "There aren't any results available for that measurement")

        results = SaganSet(iterable=results, probes=self.arguments.probes)
        if self.arguments.aggregate_by:
            results = aggregate(results, self.get_aggregators())

        description = measurement.description or ""
        if description:
            description = "\n{}\n".format(description)

        header = "RIPE Atlas Report for Measurement #{}\n" \
                 "===================================================" \
                 "{}".format(measurement.id, description)

        Rendering(renderer=renderer, header=header, payload=results).render()

    def get_aggregators(self):
        """Return aggregators list based on user input"""
        aggregation_keys = []
        for aggr_key in self.arguments.aggregate_by:
            # Get class and aggregator key
            aggregation_class = self.AGGREGATORS[aggr_key][1]
            key = self.AGGREGATORS[aggr_key][0]
            if aggr_key == "rtt-median":
                # Get range for the aggregation
                key_range = self.AGGREGATORS[aggr_key][2]
                aggregation_keys.append(
                    aggregation_class(key=key, ranges=key_range)
                )
            else:
                aggregation_keys.append(aggregation_class(key=key))
        return aggregation_keys
