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

from __future__ import print_function, absolute_import

import itertools

from ripe.atlas.cousteau import MeasurementRequest

from .base import Command as BaseCommand, TabularFieldsMixin
from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from ..helpers.validators import ArgumentType


class Command(TabularFieldsMixin, BaseCommand):

    NAME = "measurement-search"
    LIMITS = (1, 1000)

    STATUS_SPECIFIED = 0
    STATUS_SCHEDULED = 1
    STATUS_ONGOING = 2
    STATUS_STOPPED = 4
    STATUS_FORCED_STOP = 5
    STATUS_NO_SUITABLE_PROBES = 6
    STATUS_FAILED = 7
    STATUSES = {
        "scheduled": (STATUS_SPECIFIED, STATUS_SCHEDULED,),
        "ongoing": (STATUS_ONGOING,),
        "stopped": (
            STATUS_STOPPED,
            STATUS_FORCED_STOP,
            STATUS_NO_SUITABLE_PROBES,
            STATUS_FAILED,
        )
    }

    # Column name: (alignment, width)
    COLUMNS = {
        "id": ("<", 7),
        "type": ("<", 10),
        "description": ("<", 42),
        "status": (">", 18),
        "target": ("<", 45),
        "url": ("<", 45),
    }

    DESCRIPTION = (
        "Fetch and print measurements fulfilling specified criteria based "
        "on given filters"
    )

    def add_arguments(self):

        self.parser.add_argument(
            "--search",
            type=str,
            help="A search string.  This could match the target or description."
        )
        self.parser.add_argument(
            "--status",
            type=str,
            choices=self.STATUSES.keys(),
            help="The measurement status."
        )
        self.parser.add_argument(
            "--af",
            type=int,
            choices=(4, 6),
            help="The address family."
        )
        self.parser.add_argument(
            "--type",
            type=str,
            choices=("ping", "traceroute", "dns", "sslcert", "ntp", "http"),
            help="The measurement type."
        )
        self.parser.add_argument(
            "--field",
            type=str,
            action="append",
            choices=self.COLUMNS.keys(),
            default=[],
            help="The field(s) to display. Invoke multiple times for multiple "
                 "fields. The default is id, type, description, and status."
        )
        self.parser.add_argument(
            "--ids-only",
            action="store_true",
            default=False,
            help="Display a list of measurement ids matching your filter "
                 "criteria."
        )

        timing = self.parser.add_argument_group("Timing")
        for position in ("started", "stopped"):
            for chrono in ("before", "after"):
                timing.add_argument(
                    "--{}-{}".format(position, chrono),
                    type=ArgumentType.datetime,
                    help="Filter for measurements that {} {} a specific date. "
                         "The format required is YYYY-MM-DDTHH:MM:SS".format(
                             position, chrono)
                )

        self.parser.add_argument(
            "--limit",
            type=ArgumentType.integer_range(self.LIMITS[0], self.LIMITS[1]),
            default=50,
            help="The number of measurements to return.  The number must be "
                 "between {} and {}".format(self.LIMITS[0], self.LIMITS[1])
        )

    def run(self):

        if not self.arguments.field:
            self.arguments.field = ("id", "type", "description", "status")

        filters = self._get_filters()
        measurements = MeasurementRequest(
            return_objects=True, user_agent=self.user_agent, **filters)
        truncated_measurements = itertools.islice(
            measurements, self.arguments.limit)

        if self.arguments.ids_only:
            for measurement in truncated_measurements:
                print(measurement.id)
            return

        hr = self._get_horizontal_rule()

        print(self._get_filter_display(filters))
        print(self._get_header())
        print(colourise(hr, "bold"))

        for measurement in truncated_measurements:
            print(colourise(self._get_line_format().format(
                *self._get_line_items(measurement)
            ), self._get_colour_from_status(measurement.status_id)))

        print(colourise(hr, "bold"))

        # Print total count of found measurements
        print(("{:>" + str(len(hr)) + "}\n").format(
            "Showing {} of {} total measurements".format(
                min(self.arguments.limit, measurements.total_count),
                measurements.total_count
            )
        ))

    def _get_line_items(self, measurement):

        r = []

        for field in self.arguments.field:
            if field == "url":
                r.append("https://atlas.ripe.net/measurements/{}/".format(
                    measurement.id
                ))
            elif field == "type":
                r.append(measurement.type.lower())
                continue
            elif field == "target":
                r.append(sanitise(
                    measurement.target or
                    measurement.target_ip or
                    "-"
                )[:self.COLUMNS["target"][1]])
            elif field == "description":
                description = sanitise(measurement.description) or ""
                r.append(description[:self.COLUMNS["description"][1]])
            else:
                r.append(sanitise(getattr(measurement, field)))

        return r

    def _get_filters(self):

        r = {}

        if self.arguments.search:
            r["search"] = self.arguments.search
        if self.arguments.status:
            r["status__in"] = self.STATUSES[self.arguments.status]
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

    def _get_colour_from_status(self, status):
        if status in self.STATUSES["ongoing"]:
            return "green"
        if status == self.STATUS_STOPPED:
            return "yellow"
        if status in self.STATUSES["stopped"]:
            return "red"
        if status in self.STATUSES["scheduled"]:
            return "blue"
        return "white"
