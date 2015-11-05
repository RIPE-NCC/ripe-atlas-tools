from __future__ import print_function, absolute_import

from ...helpers.validators import ArgumentType
from ...settings import conf

from .base import Command


class TracerouteMeasureCommand(Command):

    def add_arguments(self):

        Command.add_arguments(self)

        spec = conf["specification"]["types"]["traceroute"]

        specific = self.parser.add_argument_group(
            "Traceroute-specific Options")
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
            "--protocol",
            type=str,
            choices=("ICMP", "UDP", "TCP"),
            default=spec["protocol"],
            help="The protocol used."
        )
        specific.add_argument(
            "--timeout",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["timeout"],
            help="The timeout per-packet"
        )
        specific.add_argument(
            "--dont-fragment",
            action="store_true",
            default=spec["dont-fragment"],
            help="Don't Fragment the packet"
        )
        specific.add_argument(
            "--paris",
            type=ArgumentType.integer_range(minimum=0, maximum=64),
            default=spec["paris"],
            help="Use Paris. Value must be between 0 and 64."
                 "If 0, a standard traceroute will be performed"
        )
        specific.add_argument(
            "--first-hop",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=spec["first-hop"],
            help="Value must be between 1 and 255"
        )
        specific.add_argument(
            "--max-hops",
            type=ArgumentType.integer_range(minimum=1, maximum=255),
            default=spec["max-hops"],
            help="Value must be between 1 and 255"
        )
        specific.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=2**16),
            default=spec["port"],
            help="Destination port, valid for TCP only"
        )
        specific.add_argument(
            "--destination-option-size",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["destination-option-size"],
            help="IPv6 destination option header"
        )
        specific.add_argument(
            "--hop-by-hop-option-size",
            type=ArgumentType.integer_range(minimum=1),
            default=spec["hop-by-hop-option-size"],
            help=" IPv6 hop by hop option header"
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        keys = (
            "destination_option_size", "dont_fragment", "first_hop",
            "hop_by_hop_option_size", "max_hops", "packets", "paris", "port",
            "protocol", "size", "timeout"
        )
        for key in keys:
            r[key] = getattr(self.arguments, key)

        return r
