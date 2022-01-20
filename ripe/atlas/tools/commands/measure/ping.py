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

from ...helpers.validators import ArgumentType
from ...settings import conf
from .base import Command


class PingMeasureCommand(Command):
    DESCRIPTION = "Create a ping measurement and wait for the results"

    def add_arguments(self):

        Command.add_arguments(self)

        self.add_primary_argument(name="target", parser=self.parser)

        spec = conf["specification"]["types"]["ping"]

        specific = self.parser.add_argument_group("Ping-specific Options")
        specific.add_argument(
            "--packets",
            type=ArgumentType.integer_range(minimum=1, maximum=16),
            default=spec["packets"],
            help="The number of packets sent",
        )
        specific.add_argument(
            "--size",
            type=ArgumentType.integer_range(minimum=1, maximum=2048),
            default=spec["size"],
            help="The size of packets sent",
        )
        specific.add_argument(
            "--packet-interval",
            type=ArgumentType.integer_range(minimum=2, maximum=30000),
            default=spec["packet-interval"],
        )
        self.add_flag(
            parser=specific,
            name="include-probe-id",
            default=spec["include_probe_id"],
            help="Include the ASCII-encoded probe ID in the ping packets",
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        r["packets"] = self.arguments.packets
        r["packet_interval"] = self.arguments.packet_interval
        r["size"] = self.arguments.size
        if self.arguments.include_probe_id:
            r["include_probe_id"] = True

        return r
