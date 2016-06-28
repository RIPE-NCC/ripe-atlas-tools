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

from ..ipdetails import IP
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    DEFAULT_RADIUS = 2

    @staticmethod
    def add_arguments(parser):
        group = parser.add_argument_group(
            title="Optional arguments for traceroute_aspath renderer"
        )
        group.add_argument(
            "--traceroute-aspath-radius",
            type=int,
            help="Number of different ASs starting from the end of the "
                 "traceroute path. "
                 "Default: {}.".format(Renderer.DEFAULT_RADIUS),
            metavar="RADIUS",
            default=Renderer.DEFAULT_RADIUS
        )

    def __init__(self, *args, **kwargs):
        BaseRenderer.__init__(self, *args, **kwargs)
        self.paths = {}

        # Number of different ASs starting from the end of the traceroute path.
        if "arguments" in kwargs:
            self.RADIUS = kwargs["arguments"].traceroute_aspath_radius
        else:
            self.RADIUS = Renderer.DEFAULT_RADIUS

    @staticmethod
    def _get_asns_for_output(asns, radius):
        asns_with_padding = [""] * radius + asns
        asns_with_padding = asns_with_padding[-radius:]
        return " ".join(
            ["{:>8}".format("AS{}".format(asn) if asn else "") for asn in asns_with_padding]
        )

    def on_start(self):
        return "For each traceroute path toward the target, the " \
               "last {} ASNs will be shown\n\n".format(self.RADIUS)

    def on_result(self, result):

        ip_hops = []

        for hop in result.hops:
            for packet in hop.packets:
                if packet.origin:
                    ip_hops.append(packet.origin)
                    break

        asns = []

        # starting from the last hop's IP, get up to <RADIUS> ASNs
        for address in reversed(ip_hops):
            ip = IP(address)
            if ip.asn and ip.asn not in asns:
                asns.append(ip.asn)
            if len(asns) == self.RADIUS:
                break

        as_path = self._get_asns_for_output(list(reversed(asns)), self.RADIUS)

        if as_path not in self.paths:
            self.paths[as_path] = {}
            self.paths[as_path]['cnt'] = 0
            self.paths[as_path]['responded'] = 0
        self.paths[as_path]['cnt'] += 1
        if result.destination_ip_responded:
            self.paths[as_path]['responded'] += 1

        return "Probe #{:<5}: {}, {}completed\n".format(
            result.probe_id, as_path,
            "NOT " if not result.destination_ip_responded else ""
        )

    def additional(self, results):
        s = "\nNumber of probes for each AS path:\n\n"

        for as_path in self.paths:
            s += "  {}: {} probe{}, {} completed\n".format(
                as_path,
                self.paths[as_path]['cnt'],
                "s" if self.paths[as_path]['cnt'] > 1 else "",
                self.paths[as_path]['responded']
            )

        return s
