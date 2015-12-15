# Copyright (c) 2015 RIPE NCC
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

import itertools

try:
    import ujson as json
except ImportError:
    import json

from ripe.atlas.sagan import Result

from ..aggregators import RangeKeyAggregator, ValueKeyAggregator, aggregate
from ..helpers.rendering import SaganSet, Rendering
from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "render"

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

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self.file = None

    def add_arguments(self):
        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers_or_file,
            help="Either a comma-separated list of probe ids you want to see "
                 "exclusively, a path to a file containing probe ids (one on "
                 "each line), or \"-\" for standard input in the same format."
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

        sample, source = self._get_sample_result_and_source(using_regular_file)

        results = SaganSet(iterable=source, probes=self.arguments.probes)
        if self.arguments.aggregate_by:
            results = aggregate(results, self.get_aggregators())

        renderer = Renderer.get_renderer(
            self.arguments.renderer, Result.get(sample).type)()

        Rendering(renderer=renderer, payload=results).render()

        if using_regular_file:
            self.file.close()

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

    def _get_sample_result_and_source(self, using_regular_file):
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
        sample = self.file.next()

        # Re-attach the line back onto the iterable so we don't lose anything
        source = itertools.chain([sample], self.file)

        # In the case of the Very Large String, we parse out the JSON here
        if sample.startswith("["):
            source = json.loads("".join(source))
            sample = source[0]  # Reassign sample to an actual result

        return sample, source
