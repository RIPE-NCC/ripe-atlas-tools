from __future__ import print_function, absolute_import

import itertools

from ripe.atlas.cousteau import MeasurementRequest

from .base import Command as BaseCommand
from ..helpers.colours import colourise
from ..helpers.validators import ArgumentType


class Command(BaseCommand):

    NAME = "measurements"
    LIMITS = (1, 1000)

    DESCRIPTION = (
        "Fetches and prints measurements fulfilling specified criteria based "
        "on given filters."
    )

    def add_arguments(self):

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

        timing = self.parser.add_argument_group("Timing")
        timing.add_argument(
            "--started-before",
            type=ArgumentType.datetime,
            help="Filter for measurements that started before a specific date. "
                 "The format required is YYYY-MM-DDTHH:MM:SS"
        )
        timing.add_argument(
            "--started-after",
            type=ArgumentType.datetime,
            help="Filter for measurements that started after a specific date. "
                 "The format required is YYYY-MM-DDTHH:MM:SS"
        )
        timing.add_argument(
            "--stopped-before",
            type=ArgumentType.datetime,
            help="Filter for measurements that stopped before a specific date. "
                 "The format required is YYYY-MM-DDTHH:MM:SS"
        )
        timing.add_argument(
            "--stopped-after",
            type=ArgumentType.datetime,
            help="Filter for measurements that stopped after a specific date. "
                 "The format required is YYYY-MM-DDTHH:MM:SS"
        )

        self.parser.add_argument(
            "--limit",
            type=ArgumentType.integer_range(self.LIMITS[0], self.LIMITS[1]),
            default=50,
            help="The number of measurements to return.  The number must be "
                 "between {} and {}".format(self.LIMITS[0], self.LIMITS[1])
        )

    def run(self):

        measurements = MeasurementRequest(**self._get_filters())

        print("\n{:<8} {:10} {:<45} {:>14}\n{}".format(
            "ID", "Type", "Description", "Status", "=" * 80
        ))
        for measurement in itertools.islice(measurements, self.arguments.limit):

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
                min(self.arguments.limit, measurements.total_count),
                measurements.total_count
            )
        ))

    def _get_filters(self):

        r = {"return_objects": True}

        if self.arguments.status:
            r["status"] = self.arguments.status
        if self.arguments.af:
            r["af"] = self.arguments.af
        if self.arguments.type:
            r["type"] = self.arguments.type
        if self.arguments.started_before:
            r["start_time__lt"] = self.arguments.started_before
        if self.arguments.started_after:
            r["start_time__gt"] = self.arguments.started_after
        if self.arguments.stopped_before:
            r["stop_time__lt"] = self.arguments.stopped_before
        if self.arguments.stopped_after:
            r["stop_time__gt"] = self.arguments.stopped_after

        return r

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
