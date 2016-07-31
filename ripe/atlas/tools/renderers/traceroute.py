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

from .base import Renderer as BaseRenderer

from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from ..ipdetails import IP


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    DEFAULT_SHOW_ASNS = False

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group(
            title="Optional arguments for traceroute renderer"
        )
        group.add_argument(
            "--traceroute-show-asns",
            help="Show Autonomous System Numbers (ASNs) in the traceroute "
                 "results.",
            action="store_true",
            default=Renderer.DEFAULT_SHOW_ASNS
        )

    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)

        if "arguments" in kwargs:
            self.show_asns = kwargs["arguments"].traceroute_show_asns
        else:
            self.show_asns = Renderer.DEFAULT_SHOW_ASNS

    def on_result(self, result):

        r = ""

        for hop in result.hops:

            if hop.is_error:
                r += "{}\n".format(
                    colourise(sanitise(hop.error_message), "red"))
                continue

            name = ""
            asn = ""
            rtts = []
            for packet in hop.packets:
                name = name or packet.origin or "*"
                if self.show_asns:
                    if packet.origin and not asn:
                        asn = IP(packet.origin).asn
                if packet.rtt:
                    rtts.append("{:8} ms".format(packet.rtt))
                else:
                    rtts.append("          *")

            if not asn:
                tpl = "{hop:>3} {name:37} {rtts}\n"
            else:
                tpl = "{hop:>3} {name:28} {asn:>8} {rtts}\n"

            r += tpl.format(
                hop=hop.index,
                name=sanitise(name),
                asn="AS{}".format(asn) if asn else "",
                rtts="  ".join(rtts)
            )

        return "\n{}\n\n{}".format(
            colourise("Probe #{}".format(result.probe_id), "bold"),
            r
        )
