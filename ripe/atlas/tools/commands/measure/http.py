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


class HttpMeasureCommand(Command):

    def add_arguments(self):

        Command.add_arguments(self)

        spec = conf["specification"]["types"]["http"]

        specific = self.parser.add_argument_group("HTTP-specific Options")
        specific.add_argument(
            "--header-bytes",
            type=ArgumentType.integer_range(minimum=0, maximum=2048),
            default=spec["header-bytes"],
            help="The maximum number of bytes to retrieve from the header"
        )
        specific.add_argument(
            "--version",
            type=str,
            default=spec["version"],
            help="The HTTP version to use"
        )
        specific.add_argument(
            "--method",
            type=str,
            default=spec["method"],
            help="The HTTP method to use"
        )
        specific.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=2**16),
            default=spec["port"],
            help="Destination port"
        )
        specific.add_argument(
            "--path",
            type=str,
            default=spec["path"],
            help=""
        )
        specific.add_argument(
            "--query-string",
            type=str,
            default=spec["query-string"],
            help=""
        )
        specific.add_argument(
            "--user-agent",
            type=str,
            default=spec["user-agent"],
            help="The user agent used when performing the request"
        )
        specific.add_argument(
            "--body-bytes",
            type=ArgumentType.integer_range(minimum=1, maximum=1020048),
            default=spec["body-bytes"],
            help="The maximum number of bytes to retrieve from the body"
        )
        specific.add_argument(
            "--timing-verbosity",
            type=int,
            choices=(0, 1, 2),
            default=spec["timing-verbosity"],
            help="The amount of timing information you want returned. 1 "
                 "returns the time to read, to connect, and to first byte, 2 "
                 "returns timing information per read system call.  0 "
                 "(default) returns no additional timing information."
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        keys = (
            "header_bytes", "version", "method", "port", "path", "query_string",
            "user_agent"
        )
        for key in keys:
            r[key] = getattr(self.arguments, key)

        if self.arguments.timing_verbosity > 0:
            r["extended_timing"] = True
            if self.arguments.timing_verbosity > 1:
                r["more_extended_timing"] = True

        r["max_bytes_read"] = self.arguments.body_bytes

        return r
