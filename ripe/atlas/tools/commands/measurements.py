from __future__ import print_function, absolute_import

import itertools

from ripe.atlas.cousteau import MeasurementRequest

from .base import Command as BaseCommand
from ..helpers.colours import colourise
from ..helpers.validators import ArgumentType


class Command(BaseCommand):

    NAME = "measurements"
    MAX_RESULTS = 50

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
            choices=("ping", "traceroute", "dns", "sslcert", "ntp", "http"),
            help="The measurement type"
        )
        self.parser.add_argument(
            "--started-before",
            type=ArgumentType.datetime,
            help=""
        )
        self.parser.add_argument(
            "--started-after",
            type=ArgumentType.datetime,
            help=""
        )

    def run(self):

        filters = {"return_objects": True}
        if self.arguments.status:
            filters["status"] = self.arguments.status
        if self.arguments.af:
            filters["af"] = self.arguments.af
        if self.arguments.type:
            filters["type"] = self.arguments.type

        measurements = MeasurementRequest(**filters)

        print("\n{:<8} {:10} {:<45} {:>14}\n{}".format(
            "ID", "Type", "Description", "Status", "=" * 80
        ))
        for measurement in itertools.islice(measurements, self.MAX_RESULTS):

            destination = measurement.destination_name or \
                measurement.destination_address or \
                ""

            print(colourise("{:<8} {:10} {:<45} {:>14}".format(
                measurement.id,
                measurement.type.lower(),
                destination[:45],
                measurement.status
            ), self._get_colour_from_status(measurement.status)))

        # Print total count of found measurements
        print("{}\n{:>80}".format(
            "=" * 80,
            "Showing {} of {} total measurements".format(
                min(self.MAX_RESULTS, measurements.total_count),
                measurements.total_count
            )
        ))

    @staticmethod
    def _get_colour_from_status(status):
        status = status.lower()
        if status == "ongoing":
            return "green"
        if status in ("failed", "forced to stop", "no suitable probes"):
            return "red"
        if status in ("specified", "scheduled"):
            return "blue"
        if status == "stopped":
            return "yellow"
        return "white"
