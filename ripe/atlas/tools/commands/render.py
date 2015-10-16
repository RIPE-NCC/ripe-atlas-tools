from __future__ import print_function

import sys

from ..aggregators import RangeKeyAggregator, ValueKeyAggregator, aggregate
from ..helpers.rendering import SaganSet, Rendering
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = "Render the contents of an arbitrary file.\n\nExample:\n" \
                  "  cat /my/file | ripe-atlas render\n"

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
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers,
            help="A comma-separated list of probe ids you want to see "
                 "exclusively."
        )
        self.parser.add_argument(
            "--from-file",
            type=ArgumentType.path,
            default="-",
            help='The source of the data to be rendered.  If nothing is '
                 'specified, we assume "-" or, standard in (the default).'
        )
        self.parser.add_argument(
            "--aggregate-by",
            type=str,
            choices=self.AGGREGATORS.keys(),
            action="append",
            help="Tell the rendering engine to aggregate the results by the "
                 "selected option.  Note that if you opt for aggregation, no "
                 "output will be generated until all results are received, and "
                 "if large data sets may explode your system."
        )

    def run(self):

        using_regular_file = self.arguments.from_file != "-"

        source = sys.stdin
        if using_regular_file:
            source = open(self.arguments.from_file)

        results = SaganSet(iterable=source, probes=self.arguments.probes)
        if self.arguments.aggregate_by:
            results = aggregate(results, self.get_aggregators())

        Rendering(renderer=self.arguments.renderer, payload=results).render()

        if using_regular_file:
            source.close()

    def get_aggregators(self):
        """
        Return aggregators list based on user input
        """

        aggregation_keys = []
        for aggr_key in self.arguments.aggregate_by:

            # Get class and aggregator key
            aggregation_class = self.AGGREGATORS[aggr_key][1]
            key = self.AGGREGATORS[aggr_key][0]
            if aggr_key == "rtt":
                # Get range for the aggregation
                key_range = self.AGGREGATORS[aggr_key][2]
                aggregation_keys.append(
                    aggregation_class(key=key, ranges=key_range)
                )
            else:
                aggregation_keys.append(aggregation_class(key=key))

        return aggregation_keys
