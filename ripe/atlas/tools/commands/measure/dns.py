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

from ripe.atlas.sagan.dns import Message

from ...exceptions import RipeAtlasToolsException
from ...helpers.validators import ArgumentType
from ...settings import conf

from .base import Command


class DnsMeasureCommand(Command):

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

        specific = self.parser.add_argument_group("DNS-specific Options")
        specific.add_argument(
            "--protocol",
            type=self._upper_str,
            choices=("UDP", "TCP"),
            default=conf["specification"]["types"]["dns"]["protocol"],
            help="The protocol used."
        )
        specific.add_argument(
            "--query-class",
            type=self._upper_str,
            choices=("IN", "CHAOS"),
            default=conf["specification"]["types"]["dns"]["query-class"],
            help='The query class.  The default is "{}"'.format(
                conf["specification"]["types"]["dns"]["query-class"]
            )
        )
        specific.add_argument(
            "--query-type",
            type=self._upper_str,
            choices=list(Message.ANSWER_CLASSES.keys()) + ["ANY"],  # The only ones we can parse
            default=conf["specification"]["types"]["dns"]["query-type"],
            help='The query type.  The default is "{}"'.format(
                conf["specification"]["types"]["dns"]["query-type"]
            )
        )
        specific.add_argument(
            "--query-argument",
            type=str,
            default=conf["specification"]["types"]["dns"]["query-argument"],
            help="The DNS label to query"
        )
        specific.add_argument(
            "--set-cd-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-cd-bit"],
            help="Set the DNSSEC Checking Disabled flag (RFC4035)"
        )
        specific.add_argument(
            "--set-do-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-do-bit"],
            help="Set the DNSSEC OK flag (RFC3225)"
        )
        specific.add_argument(
            "--set-nsid-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-nsid-bit"],
            help="Include an EDNS name server ID request with the query"
        )
        specific.add_argument(
            "--set-rd-bit",
            action="store_true",
            default=conf["specification"]["types"]["dns"]["set-rd-bit"],
            help="Set the Recursion Desired flag"
        )
        specific.add_argument(
            "--retry",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["dns"]["retry"],
            help="Number of times to retry"
        )
        specific.add_argument(
            "--udp-payload-size",
            type=ArgumentType.integer_range(minimum=1),
            default=conf["specification"]["types"]["dns"]["udp-payload-size"],
            help="May be any integer between 512 and 4096 inclusive"
        )

    def clean_target(self):
        """
        Targets aren't required for this type
        """
        return self.arguments.target

    def clean_description(self):
        if self.arguments.target:
            return Command.clean_description(self)
        return "DNS measurement for {}".format(self.arguments.query_argument)

    def _get_measurement_kwargs(self):

        r = Command._get_measurement_kwargs(self)

        for opt in ("class", "type", "argument"):
            if not getattr(self.arguments, "query_{0}".format(opt)):
                raise RipeAtlasToolsException(
                    "At a minimum, DNS measurements require a query argument.")

        r["query_class"] = self.arguments.query_class
        r["query_type"] = self.arguments.query_type
        r["query_argument"] = self.arguments.query_argument
        r["set_cd_bit"] = self.arguments.set_cd_bit
        r["set_do_bit"] = self.arguments.set_do_bit
        r["set_rd_bit"] = self.arguments.set_rd_bit
        r["set_nsid_bit"] = self.arguments.set_nsid_bit
        r["protocol"] = self.arguments.protocol
        r["retry"] = self.arguments.retry
        r["udp_payload_size"] = self.arguments.udp_payload_size
        r["use_probe_resolver"] = "target" not in r

        return r
