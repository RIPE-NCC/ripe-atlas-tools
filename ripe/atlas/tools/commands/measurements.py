from __future__ import print_function, absolute_import
import sys
import requests

from ripe.atlas.cousteau import MeasurementRequest
from ripe.atlas.tools.aggregators import ValueKeyAggregator, aggregate

from ..exceptions import RipeAtlasToolsException
from ..renderers.probes import Renderer
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "probes"

    DESCRIPTION = (
        "Fetches and prints measurements fulfilling specified criteria based "
        "on given filters."
    )

    def add_arguments(self):
        """Adds all commands line arguments for this command."""
        self.parser.add_argument(
            "--search",
            type=str,
            help="A search string.  This could match the target or description"
        )
        self.parser.add_argument(
            "--status",
            type=str,
            choices=("scheduled", "ongoing", "stopped"),
            help="The measurement status"
        )
        self.parser.add_argument(
            "--af",
            type=int,
            choices=(4, 6),
            help="The address family"
        )
        self.parser.add_argument(
            "--type",
            type=str,
            choices=("ping", "traceroute", "dns", "ssl", "ntp", "http"),
            help="The measurement type"
        )

    def run(self):

        filters = {"return_objects": True}
        if self.arguments.status:
            filters["status"] = 1
        if self.arguments.af:
            filters["af"] = self.arguments.af
        if self.arguments.type:
            filters["type"] = self.arguments.type
        measurements = MeasurementRequest(**filters)

        for measurement in measurements:
            print(measurement.id)

        # Print total count of found measurements
        print(measurements.total_count)
