from __future__ import print_function, absolute_import

from ...helpers.validators import ArgumentType
from ...settings import conf

from .base import Command


class SslcertMeasureCommand(Command):

    def add_arguments(self):

        Command.add_arguments(self)

        spec = conf["specification"]["types"]["sslcert"]

        specific = self.parser.add_argument_group(
            "SSL Certificate-specific Options")
        specific.add_argument(
            "--port",
            type=ArgumentType.integer_range(minimum=1, maximum=2**16),
            default=spec["port"],
            help="Destination port"
        )

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)
        r["port"] = self.arguments.port

        return r
