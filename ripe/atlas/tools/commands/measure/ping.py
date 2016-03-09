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

from ...helpers.validators import ArgumentType
from ...settings import conf
from .base import Command


class PingMeasureCommand(Command):

    def add_arguments(self):

        Command.add_arguments(self)

        spec = conf["specification"]["types"]["ping"]

        specific = self.parser.add_argument_group("Ping-specific Options")
        specific.add_argument(
            "--packets",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["packets"],
            help="The number of packets sent"
        )
        specific.add_argument(
            "--size",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["size"],
            help="The size of packets sent"
        )
        specific.add_argument(
            "--packet-interval",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["packet-interval"],
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        r["packets"] = self.arguments.packets
        r["packet_interval"] = self.arguments.packet_interval
        r["size"] = self.arguments.size

        return r
