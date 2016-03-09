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


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    def on_result(self, result):

        packets = result.packets

        if not packets:
            return "No packets found\n"

        # Because the origin value is more reliable as "from" in v4 and as
        # "packet.source_address" in v6.
        origin = result.origin
        if ":" in origin:
            origin = packets[0].source_address

        line = "{} bytes from probe #{:<5} {:15} to {} ({}): ttl={} times:{}\n"
        return line.format(
            result.packet_size,
            result.probe_id,
            origin,
            result.destination_name,
            result.destination_address,
            packets[0].ttl,
            " ".join(["{:8}".format(str(_.rtt) + ",") for _ in packets])
        )
