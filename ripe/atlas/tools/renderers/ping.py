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

from ..helpers.sanitisers import sanitise
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):
    """
    This is meant to be a stub example for what an aggregate renderer might look
    like. If you have ideas as to how to make this better, feel free to send
    along a pull request.
    """

    RENDERS = [BaseRenderer.TYPE_PING]

    def __init__(self, **kwargs):
        BaseRenderer.__init__(self, **kwargs)

        self.target = ""
        self.packet_loss = 0
        self.sent_packets = 0
        self.received_packets = 0
        self.rtts = []
        self.rtts_min = []
        self.rtts_max = []
        self.rtt_types_map = {"min": self.rtts_min, "max": self.rtts_max}

    def collect_stats(self, result):
        """
        Calculates, stores and collects all stats we want from the given
        result.
        """
        if not self.target:
            self.target = result.destination_name
        self.sent_packets += result.packets_sent
        self.received_packets += result.packets_received
        self.collect_min_max_rtts("min", result.rtt_min)
        self.collect_min_max_rtts("max", result.rtt_max)

        self.collect_packets_rtt(result.packets)

    def collect_min_max_rtts(self, rtt_type, rtt):
        """
        Stores the given rtt in the corresponding list (min/max) if rtt is set.
        """
        rtt = rtt
        if not rtt:
            rtt = 0

        self.rtt_types_map[rtt_type].append(rtt)

    def collect_packets_rtt(self, packets):
        """
        Collects all the rrts of given packets and stores them
        in our rtts list.
        """
        for packet in packets:
            rtt = packet.rtt
            if not packet.rtt:
                rtt = 0
            self.rtts.append(rtt)

    def calculate_loss(self):
        """Calculates the total loss between received and sent packets."""
        if not self.sent_packets:
            return 0

        return (1 - float(self.received_packets) / self.sent_packets) * 100

    def mean(self):
        """Calculates the mean of the collected rtts"""
        return round(float(sum(self.rtts)) / max(len(self.rtts), 1), 3)

    def median(self):
        """Calculates the median of the collected rtts"""
        sorted_rtts = sorted(self.rtts)
        index = (len(self.rtts) - 1) // 2
        if len(self.rtts) % 2:
            return sorted_rtts[index]
        else:
            return (sorted_rtts[index] + sorted_rtts[index + 1]) / 2.0

    def on_result(self, result):
        packets = result.packets

        if not packets:
            return "No packets found\n"

        self.collect_stats(result)

        # Because the origin value is more reliable as "from" in v4 and as
        # "packet.source_address" in v6.
        origin = result.origin
        if ":" in origin:
            origin = packets[0].source_address

        times = ", ".join([str(_.rtt) + " ms" for _ in packets])

        return (
            f"{result.packet_size} bytes from {result.destination_address} via "
            f"probe #{result.probe_id} ({origin})"
            f": ttl={packets[0].ttl} times={times}\n"
        )

    def header(self, sample):
        resolved_on = (
            "server"
            if sample.destination_address == sample.destination_name
            else "probe"
        )
        return f"PING {sample.destination_name} (resolved on {resolved_on})\n"

    def footer(self):
        if not self.sent_packets:
            return ""
        self.packet_loss = self.calculate_loss()
        return self.render_template(
            "reports/aggregate_ping.txt",
            target=sanitise(self.target),
            sent=self.sent_packets,
            received=self.received_packets,
            packet_loss=self.packet_loss,
            min=min(self.rtts_min),
            median=self.median(),
            mean=self.mean(),
            max=max(self.rtts_max),
        )
