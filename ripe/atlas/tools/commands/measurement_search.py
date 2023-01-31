# Copyright (c) 2023 RIPE NCC
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

import itertools
from typing import Dict

from ripe.atlas.cousteau import MeasurementRequest

from ..helpers import tabular
from ..helpers.sanitisers import sanitise
from ..helpers.validators import ArgumentType
from ..settings import conf
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "measurement-search"
    LIMITS = (1, 10000)
    MAX_PAGE_SIZE = 500  # Request chunks of this size or smaller

    STATUS_SPECIFIED = 0
    STATUS_SCHEDULED = 1
    STATUS_ONGOING = 2
    STATUS_STOPPED = 4
    STATUS_FORCED_STOP = 5
    STATUS_NO_SUITABLE_PROBES = 6
    STATUS_FAILED = 7
    STATUSES = {
        "scheduled": (
            STATUS_SPECIFIED,
            STATUS_SCHEDULED,
        ),
        "ongoing": (STATUS_ONGOING,),
        "stopped": (
            STATUS_STOPPED,
            STATUS_FORCED_STOP,
            STATUS_NO_SUITABLE_PROBES,
            STATUS_FAILED,
        ),
    }

    COLUMNS: Dict[str, tabular.ColumnDef] = {
        "id": {"align": ">", "width": 7},
        "type": {"align": "^", "width": 10},
        "description": {"align": "^", "width": 42},
        "status": {"align": "^", "width": 18},
        "target": {"align": ">", "width": 45},
        "url": {"align": "^", "width": 45},
    }

    DESCRIPTION = (
        "Fetch and print measurements fulfilling specified criteria based "
        "on given filters"
    )

    def add_arguments(self) -> None:
        self.parser.add_argument(
            "--search",
            type=str,
            help="A search string.  This could match the target or description.",
        )
        self.parser.add_argument(
            "--status",
            type=str,
            choices=self.STATUSES.keys(),
            help="The measurement status.",
        )
        self.parser.add_argument(
            "--af", type=int, choices=(4, 6), help="The address family."
        )
        self.parser.add_argument(
            "--type",
            type=str,
            choices=("ping", "traceroute", "dns", "sslcert", "ntp", "http"),
            help="The measurement type.",
        )

        timing = self.parser.add_argument_group("Timing")
        for position in ("started", "stopped"):
            for chrono in ("before", "after"):
                timing.add_argument(
                    "--{}-{}".format(position, chrono),
                    type=ArgumentType.datetime,
                    help="Filter for measurements that {} {} a specific date. "
                    "The format required is YYYY-MM-DDTHH:MM:SS".format(
                        position, chrono
                    ),
                )

        self.parser.add_argument(
            "--limit",
            type=ArgumentType.integer_range(self.LIMITS[0], self.LIMITS[1]),
            default=50,
            help="The number of measurements to return.  The number must be "
            "between {} and {}".format(self.LIMITS[0], self.LIMITS[1]),
        )
        tabular.add_argument_group(self.parser, self.COLUMNS.keys())

    def run(self) -> None:
        if not self.arguments.field:
            self.arguments.field = ["id", "type", "description", "status"]

        request_fields = list(
            set(self.arguments.field) | set(self.arguments.aggregate_by)
        )
        if "status" not in request_fields:
            request_fields.append("status")

        filters = self._get_filters()
        measurements = MeasurementRequest(
            server=conf["api-server"],
            return_objects=True,
            user_agent=self.user_agent,
            fields=",".join(request_fields),
            page_size=min(self.MAX_PAGE_SIZE, self.arguments.limit),
            **filters,
        )
        truncated_measurements = itertools.islice(measurements, self.arguments.limit)

        renderer = tabular.renderers[self.arguments.format]

        rows = [self._get_row(m) for m in truncated_measurements]

        for line in renderer(
            rows=rows,
            total_count=measurements.total_count,
            columns=dict((c, self.COLUMNS[c]) for c in self.arguments.field),
            filters=filters,
            arguments=self.arguments,
        ):
            print(line)

    def _get_row(self, measurement) -> tabular.RowDef:
        r = {}

        for field in self.arguments.field + self.arguments.aggregate_by:
            if field == "url":
                r["url"] = f"https://atlas.ripe.net/measurements/{measurement.id}/"
            elif field == "type":
                r["type"] = measurement.type.lower()
            elif field == "target":
                r["target"] = sanitise(
                    measurement.target or measurement.target_ip or "-"
                )
            elif field == "description":
                r["description"] = sanitise(measurement.description) or ""
            else:
                r[field] = sanitise(getattr(measurement, field))

        return {
            "values": r,
            "colour": self._get_colour_from_status(measurement.status_id),
        }

    def _get_filters(self) -> Dict[str, str]:

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

    def _get_colour_from_status(self, status: int) -> str:
        if status in self.STATUSES["ongoing"]:
            return "green"
        if status == self.STATUS_STOPPED:
            return "yellow"
        if status in self.STATUSES["stopped"]:
            return "red"
        if status in self.STATUSES["scheduled"]:
            return "blue"
        return "white"
