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


class SslcertMeasureCommand(Command):
    DESCRIPTION = "Create a TLS (SSL) cert measurement and wait for the results"

    def add_arguments(self):

        Command.add_arguments(self)

        self.add_primary_argument(name="target", parser=self.parser)

        spec = conf["specification"]["types"]["sslcert"]

        specific = self.parser.add_argument_group("SSL Certificate-specific Options")
        specific.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=65535),
            default=spec["port"],
            help="Destination port",
        )
        specific.add_argument(
            "--hostname",
            default=spec["hostname"],
            type=str,
            help="SNI Hostname",
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)
        r["port"] = self.arguments.port
        if self.arguments.hostname:
            r["hostname"] = self.arguments.hostname

        return r
