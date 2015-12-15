# Copyright (c) 2015 RIPE NCC
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
from .base import Result

from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_TRACEROUTE]

    def on_result(self, result):

        r = ""

        for hop in result.hops:

            if hop.is_error:
                r += "{}\n".format(
                    colourise(sanitise(hop.error_message), "red"))
                continue

            name = ""
            rtts = []
            for packet in hop.packets:
                name = name or packet.origin or "*"
                if packet.rtt:
                    rtts.append("{:8} ms".format(packet.rtt))
                else:
                    rtts.append("          *")

            r += "{:>3} {:39} {}\n".format(
                hop.index,
                sanitise(name),
                "  ".join(rtts)
            )

        return Result(
            "\n{}\n\n{}".format(
                colourise("Probe #{}".format(result.probe_id), "bold"),
                r
            ),
            result.probe_id
        )
