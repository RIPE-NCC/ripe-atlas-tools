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


class TracerouteMeasureCommand(Command):
    DESCRIPTION = "Create a traceroute measurement and wait for the results"

    def _upper_str(self, s):
        """
        Private method to validate specific command line arguments that
        should be provided in upper or lower case
        :param s: string
        :return: string in upper case
        """
        return s.upper()

    def add_arguments(self):

        Command.add_arguments(self)

        self.add_primary_argument(name="target", parser=self.parser)

        spec = conf["specification"]["types"]["traceroute"]

        specific = self.parser.add_argument_group("Traceroute-specific Options")
        specific.add_argument(
            "--packets",
            type=ArgumentType.integer_range(minimum=1, maximum=16),
            default=spec["packets"],
            help="The number of packets sent",
        )
        specific.add_argument(
            "--size",
            type=ArgumentType.integer_range(minimum=0, maximum=2048),
            default=spec["size"],
            help="The size of packets sent",
        )
        specific.add_argument(
            "--protocol",
            type=self._upper_str,
            choices=("ICMP", "UDP", "TCP"),
            default=spec["protocol"],
            help="The protocol used.",
        )
        specific.add_argument(
            "--timeout",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["timeout"],
            help="The timeout per-packet",
        )
        self.add_flag(
            parser=specific,
            name="dont-fragment",
            default=spec["dont-fragment"],
            help="Disable fragmentation of outgoing packets",
        )
        specific.add_argument(
            "--paris",
            type=ArgumentType.integer_range(minimum=0, maximum=64),
            default=spec["paris"],
            help="Use Paris. Value must be between 0 and 64."
            "If 0, a standard traceroute will be performed",
        )
        specific.add_argument(
            "--first-hop",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=spec["first-hop"],
            help="Value must be between 1 and 255",
        )
        specific.add_argument(
            "--max-hops",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=spec["max-hops"],
            help="Value must be between 1 and 255",
        )
        specific.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=65535),
            default=spec["port"],
            help="Destination port, valid for TCP only",
        )
        specific.add_argument(
            "--destination-option-size",
            type=ArgumentType.integer_range(minimum=0, maximum=1024),
            default=spec["destination-option-size"],
            help="IPv6 destination option header",
        )
        specific.add_argument(
            "--hop-by-hop-option-size",
            type=ArgumentType.integer_range(minimum=0, maximum=2048),
            default=spec["hop-by-hop-option-size"],
            help=" IPv6 hop by hop option header",
        )
        specific.add_argument(
            "--duplicate-timeout",
            default=spec["duplicate-timeout"],
            type=int,
            help="Time to wait (in milliseconds) for a duplicate response "
            "after receiving the first response",
        )
        specific.add_argument(
            "--response-timeout",
            default=spec["response-timeout"],
            type=ArgumentType.integer_range(minimum=1, maximum=60000),
            help="Response timeout for one packet",
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        keys = (
            "destination_option_size",
            "dont_fragment",
            "first_hop",
            "hop_by_hop_option_size",
            "max_hops",
            "packets",
            "paris",
            "port",
            "protocol",
            "size",
            "timeout",
        )
        for key in keys:
            r[key] = getattr(self.arguments, key)
        optional_keys = ["duplicate_timeout", "response_timeout"]
        for key in optional_keys:
            val = getattr(self.arguments, key)
            if val is not None:
                r[key] = val

        return r
