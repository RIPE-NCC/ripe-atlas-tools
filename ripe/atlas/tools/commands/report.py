from __future__ import print_function

from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.sagan import Result

from ..aggregators import RangeKeyAggregator, ValueKeyAggregator, aggregate
from ..exceptions import RipeAtlasToolsException
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand
from ..probes import Probe


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = "Report the results of a measurement.\n\nExample:\n" \
                  "  ripe-atlas report 1001 --probes 157,10006\n"
    URLS = {
        "detail": "/api/v2/measurements/{}.json",
        "latest": "/api/v2/measurements/{}/latest.json",
    }
    AGGREGATORS = {
        "country": ["probe.country_code", ValueKeyAggregator],
        "rtt-median": ["rtt_median", RangeKeyAggregator, [10, 20, 30, 40, 50, 100, 200, 300]],
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
                 "exclusively"
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

    def get_probes(self):
        if self.arguments.probes:
            return [int(i) for i in self.arguments.probes.split(",")]
        return []

    def run(self):

        self.payload = ""
        pk = self.arguments.measurement_id
        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]

        self.renderer = Renderer.get_renderer(
            self.arguments.renderer, detail["type"]["name"])()

        latest_url = self.URLS["latest"].format(pk)
        if self.arguments.probes:
            latest_url += "?probes={0}".format(self.arguments.probes)

        results = AtlasRequest(url_path=latest_url).get()[1]

        if not results:
            raise RipeAtlasToolsException(
                "There aren't any results available for that measurement")

        description = detail["description"] or ""
        if description:
            description = "\n{0}\n\n".format(description)

        sagans = self.create_enhanced_sagans(results)

        if self.arguments.aggregate_by:
            aggregators = self.get_aggregators()
            enhanced_results = aggregate(sagans, aggregators)
        else:
            enhanced_results = sagans

        self.multi_level_render(enhanced_results)

        print(self.renderer.render(
            "reports/base.txt",
            measurement_id=self.arguments.measurement_id,
            description=description,
            payload=self.payload
        ), end="")

    def get_aggregators(self):
        """Return aggregators list based on user input"""
        aggregation_keys = []
        for aggr_key in self.arguments.aggregate_by:
            if aggr_key == "rtt":
                # Get class, aggregator key and range for the aggregation
                aggregation_keys.append(
                    self.AGGREGATORS[aggr_key][1](key=self.AGGREGATORS[aggr_key][0], ranges=self.AGGREGATORS[aggr_key][2])
                )
            else:
                # Get class, aggregator key
                aggregation_keys.append(self.AGGREGATORS[aggr_key][1](key=self.AGGREGATORS[aggr_key][0]))
        return aggregation_keys

    def create_enhanced_sagans(self, results):
        """Create Sagan Result objects and add additonal Probe attribute to each one of them."""
        # Sagans
        sagans = []
        for result in results:
            sagans.append(
                Result.get(
                    result,
                    on_error=Result.ACTION_IGNORE,
                    on_malformation=Result.ACTION_IGNORE
                )
            )

        # Probes
        probes = self.get_probes()
        if not probes:
            probes = set([r.probe_id for r in sagans])
        probe_objects = Probe.get_many(probes)
        probes_dict = {}
        for probe in probe_objects:
            probes_dict[probe.id] = probe

        # Populate probe attrs to sagans
        for sagan in sagans:
            sagan.probe = probes_dict[sagan.probe_id]

        return sagans

    def multi_level_render(self, aggregation_data, indent=""):
        """Traverses through aggregation data and print them indented"""

        if isinstance(aggregation_data, dict):

            for k, v in aggregation_data.items():
                self.payload = "{}{}{}\n".format(self.payload, indent, k)
                self.multi_level_render(v, indent=indent + " ")

        elif isinstance(aggregation_data, list):

            for index, data in enumerate(aggregation_data):
                self.payload = "{}{} {}".format(self.payload, indent, self.renderer.on_result(data))
