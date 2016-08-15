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

from __future__ import print_function

import sys
try:
    import ujson as json
except ImportError:
    import json
import itertools

from ripe.atlas.sagan import Result
from ripe.atlas.cousteau import (
    AtlasLatestRequest, AtlasResultsRequest
)

from ..aggregators import RangeKeyAggregator, ValueKeyAggregator, aggregate
from ..exceptions import RipeAtlasToolsException
from ..helpers.rendering import SaganSet, Rendering
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand
from ..filters import FilterFactory, filter_results
from ..settings import conf


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = (
        "Report the results of an existing measurement from the API, "
        "a file or standard input"
    )
    EXTRA_DESCRIPTION = (
        "Examples:\n"
        "  ripe-atlas report 1001 --probes 157,10006\n"
        "  ripe-atlas report --from-file results.json\n"
        "  cat results.json | ripe-atlas report --aggregate-by prefix_v4\n"
    )

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
            type=ArgumentType.msm_id_or_name(),
            help="The measurement ID or alias to fetch from the results API. "
            "(Conflicts with the --from-file option)",
            nargs="?",
        )
        self.parser.add_argument(
            "--auth",
            type=str,
            choices=conf["authorisation"]["fetch_aliases"].keys(),
            help="The API key alias you want to use to fetch the measurement. "
                 "To configure an API key alias, use "
                 "ripe-atlas configure --set authorisation.fetch_aliases."
                 "ALIAS_NAME=YOUR_KEY"
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers_or_file,
            help="Either a comma-separated list of probe ids you want to see "
                 "exclusively, a path to a file containing probe ids (one on "
                 "each line), or \"-\" for standard input in the same format."
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
                 "selected option. Note that if you opt for aggregation, no "
                 "output will be generated until all results are received."
        )
        self.parser.add_argument(
            "--probe-asns",
            type=ArgumentType.comma_separated_integers(
                minimum=1,
                # http://www.iana.org/assignments/as-numbers/as-numbers.xhtml
                maximum=2 ** 32 - 2
            ),
            help="A comma-separated list of probe ASNs you want to see "
                 "exclusively."
        )
        self.parser.add_argument(
            "--start-time",
            type=ArgumentType.datetime,
            help="The start time of the report."
        )
        self.parser.add_argument(
            "--stop-time",
            type=ArgumentType.datetime,
            help="The stop time of the report."
        )

        self.parser.add_argument(
            "--from-file",
            type=ArgumentType.path,
            help='The source of the data to be rendered. '
            '(Conflicts with specifying measurement_id)',
        )

        Renderer.add_arguments_for_available_renderers(self.parser)

    def _get_request_auth(self):
        if self.arguments.auth:
            return conf["authorisation"]["fetch_aliases"][self.arguments.auth]
        else:
            return conf["authorisation"]["fetch"]

    def _get_request(self):

        kwargs = {
            "msm_id": self.arguments.measurement_id,
            "user_agent": self.user_agent
        }
        kwargs["key"] = self._get_request_auth()
        if self.arguments.probes:
            kwargs["probe_ids"] = self.arguments.probes
        if self.arguments.start_time:
            kwargs["start"] = self.arguments.start_time
        if self.arguments.stop_time:
            kwargs["stop"] = self.arguments.stop_time

        if "start" in kwargs or "stop" in kwargs:
            return AtlasResultsRequest(**kwargs)
        return AtlasLatestRequest(**kwargs)

    def run(self):
        if self.arguments.measurement_id and self.arguments.from_file:
            raise RipeAtlasToolsException(
                "You can only specify one of --from-file or "
                "measurement_id, not both."
            )
        if self.arguments.measurement_id:
            results, sample = self._get_results_from_api(
                self.arguments.measurement_id
            )
            use_regular_file = False
        else:
            if self.arguments.from_file:
                use_regular_file = self.arguments.from_file != "-"
            elif sys.stdin.isatty():
                self.parser.print_help()
                sys.exit(1)
            else:
                use_regular_file = False

            results, sample = self._get_results_from_file(
                use_regular_file
            )

        # Sagan calls measurements "ssl" when they are actually "sslcert"
        # so we use .raw_data once we have verified and parsed the sample.
        measurement_type = Result.get(sample).raw_data["type"].lower()

        renderer = Renderer.get_renderer(
            self.arguments.renderer, measurement_type
        )(arguments=self.arguments)

        results = SaganSet(iterable=results, probes=self.arguments.probes)

        if self.arguments.probe_asns:
            asn_filters = set([])
            for asn in self.arguments.probe_asns:
                asn_filters.add(FilterFactory.create("asn", asn))
            results = filter_results(asn_filters, list(results))

        if self.arguments.aggregate_by:
            results = aggregate(results, self.get_aggregators())

        Rendering(renderer=renderer, payload=results).render()

        if use_regular_file:
            self.file.close()

    def _get_results_from_api(self, measurement_id):

        results = self._get_request().get()[1]
        if isinstance(results, list):
            if not results:
                raise RipeAtlasToolsException(
                    "There aren't any results for your request.")
        else:
            error = results.get("error")
            msg = "Error fetching measurement results"
            if error:
                msg += ": [{status} {title}] {detail}".format(
                    **error
                )
            else:
                msg = "{} Error fetching measurement results".format(error)
            raise RipeAtlasToolsException(msg)
        sample = results[0]
        return results, sample

    def _get_results_from_file(self, using_regular_file):
        """
        We need to get the first result from the source in order to detect the
        type.  Additionally, if the source is actually one great big JSON list,
        then we need to parse it so we iterate over the results since there's no
        newline characters.
        """

        self.file = sys.stdin
        if using_regular_file:
            self.file = open(self.arguments.from_file)

        # Pop the first line off the source stack.  This may very well be a Very
        # Large String and cause a memory explosion, but we like to let our
        # users shoot themselves in the foot.
        sample = next(self.file)

        # Re-attach the line back onto the iterable so we don't lose anything
        results = itertools.chain([sample], self.file)

        # In the case of the Very Large String, we parse out the JSON here
        if sample.startswith("["):
            results = json.loads("".join(results))
            sample = results[0]  # Reassign sample to an actual result

        return results, sample

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
