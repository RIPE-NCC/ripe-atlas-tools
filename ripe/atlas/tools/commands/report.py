from __future__ import print_function

from ripe.atlas.cousteau import AtlasRequest

from ..aggregators.country import CountryAggregator
from ..aggregators.simple import SimpleAggregator
from ..exceptions import RipeAtlasToolsException
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{0}.json",
        "latest": "/api/v2/measurements/{0}/latest.json",
    }
    AGGREGATORS = {
        "simple": SimpleAggregator,
        "country": CountryAggregator,
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
            choices=self.AGGREGATORS.keys(),
            default="simple",
            help="Tell the rendering engine to aggregate the results by the "
                 "selected option.  Note that if you opt for aggregation, no "
                 "output will be generated until all results are received."
        )

    def get_probes(self):
        if self.arguments.probes:
            return [int(i) for i in self.arguments.probes.split(",")]
        return []

    def run(self):

        pk = self.arguments.measurement_id
        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]

        renderer = Renderer.get_renderer(
            self.arguments.renderer, detail["type"]["name"])()

        probes = self.get_probes()

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

        print(renderer.render(
            "reports/base.txt",
            measurement_id=self.arguments.measurement_id,
            description=description,
            payload=self._get_payload(renderer, results, probes)
        ), end="")

    def _get_payload(self, renderer, results, probes):
        aggregator = self.arguments.aggregate_by
        return self.AGGREGATORS[aggregator](renderer).aggregate(
            results, probes)
