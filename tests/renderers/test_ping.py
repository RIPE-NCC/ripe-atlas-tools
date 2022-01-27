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

import unittest

from collections import namedtuple

from ripe.atlas.sagan import Result
from ripe.atlas.tools.renderers.ping import Renderer


class TestPingRenderer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.basic = Result.get(
            '{"af":4,"prb_id":1,"result":[{"rtt":10.001},{"rtt":10.002},{"rtt":10.003}],"ttl":20,"avg":10.002,"size":20,"from":"1.2.3.4","proto":"ICMP","timestamp":1440000000,"dup":0,"type":"ping","sent":3,"msm_id":1000001,"fw":4700,"max":10.003,"step":360,"src_addr":"2.3.4.5","rcvd":3,"msm_name":"Ping","lts":40,"dst_name":"my.name.ca","min":10.001,"dst_addr":"3.4.5.6"}'  # noqa: E501
        )
        self.no_packets = Result.get(
            '{"af":4,"prb_id":2,"result":[],"ttl":20,"avg":10.002,"size":20,"from":"1.2.3.4","proto":"ICMP","timestamp":1440000000,"dup":0,"type":"ping","sent":3,"msm_id":1000001,"fw":4700,"max":null,"step":360,"src_addr":"2.3.4.5","rcvd":0,"msm_name":"Ping","lts":40,"dst_name":"my.name.ca","min":null,"dst_addr":"3.4.5.6"}'  # noqa: E501
        )

    def test_basic(self):
        self.assertEqual(
            Renderer().on_result(self.basic),
            "20 bytes from 3.4.5.6 via probe #1 (1.2.3.4): ttl=20 times=10.001 ms, 10.002 ms, 10.003 ms\n",  # noqa: E501
        )

    def test_no_packets(self):
        self.assertEqual(Renderer().on_result(self.no_packets), "No packets found\n")


class TestAggregatePing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = [
            {
                u"af": 4,
                u"prb_id": 11421,
                u"result": [
                    {u"rtt": 42.342895},
                    {u"rtt": 42.220215},
                    {u"rtt": 42.40614},
                ],
                u"ttl": 53,
                u"avg": 42.3230833333,
                u"size": 48,
                u"from": u"178.11.85.39",
                u"proto": u"ICMP",
                u"timestamp": 1446146495,
                u"dup": 0,
                u"type": u"ping",
                u"sent": 3,
                u"msm_id": 2882184,
                u"fw": 4720,
                u"max": 42.40614,
                u"step": 240,
                u"src_addr": u"192.168.2.101",
                u"rcvd": 3,
                u"msm_name": u"Ping",
                u"lts": 3,
                u"dst_name": u"194.88.241.228",
                u"min": 42.220215,
                u"group_id": 2882184,
                u"dst_addr": u"194.88.241.228",
            },
            {
                u"af": 4,
                u"prb_id": 11779,
                u"result": [{u"rtt": 76.61127}, {u"rtt": 76.38997}, {u"rtt": 76.47354}],
                u"ttl": 51,
                u"avg": 76.4915933333,
                u"size": 48,
                u"from": u"79.106.99.242",
                u"proto": u"ICMP",
                u"timestamp": 1446146494,
                u"dup": 0,
                u"type": u"ping",
                u"sent": 3,
                u"msm_id": 2882184,
                u"fw": 4720,
                u"max": 76.61127,
                u"step": 240,
                u"src_addr": u"192.168.1.110",
                u"rcvd": 3,
                u"msm_name": u"Ping",
                u"lts": 127,
                u"dst_name": u"194.88.241.228",
                u"min": 76.38997,
                u"group_id": 2882184,
                u"dst_addr": u"194.88.241.228",
            },
            {
                u"af": 4,
                u"prb_id": 17854,
                u"result": [{u"rtt": 154.118}, {u"rtt": 154.197}, {u"rtt": 154.845}],
                u"ttl": 55,
                u"avg": 154.3866666667,
                u"size": 48,
                u"from": u"134.202.20.3",
                u"proto": u"ICMP",
                u"timestamp": 1446146493,
                u"dup": 0,
                u"type": u"ping",
                u"sent": 3,
                u"msm_id": 2882184,
                u"fw": 4700,
                u"max": 154.845,
                u"step": 240,
                u"src_addr": u"134.202.20.3",
                u"rcvd": 3,
                u"msm_name": u"Ping",
                u"lts": 1,
                u"dst_name": u"194.88.241.228",
                u"min": 154.118,
                u"group_id": 2882184,
                u"dst_addr": u"194.88.241.228",
            },
            {
                u"af": 4,
                u"prb_id": 3183,
                u"result": [
                    {u"rtt": 42.263816},
                    {u"rtt": 42.196233},
                    {u"rtt": 42.342921},
                ],
                u"ttl": 56,
                u"avg": 42.2676566667,
                u"size": 48,
                u"from": u"212.122.42.107",
                u"proto": u"ICMP",
                u"timestamp": 1446146494,
                u"dup": 0,
                u"type": u"ping",
                u"sent": 3,
                u"msm_id": 2882184,
                u"fw": 4720,
                u"max": 42.342921,
                u"step": 240,
                u"src_addr": u"192.168.189.1",
                u"rcvd": 3,
                u"msm_name": u"Ping",
                u"lts": 3,
                u"dst_name": u"194.88.241.228",
                u"min": 42.196233,
                u"group_id": 2882184,
                u"dst_addr": u"194.88.241.228",
            },
            {
                u"af": 4,
                u"prb_id": 3207,
                u"result": [
                    {u"rtt": 218.077484},
                    {u"rtt": 36.921608},
                    {u"rtt": 38.99444},
                ],
                u"ttl": 49,
                u"avg": 97.997844,
                u"size": 48,
                u"from": u"134.3.245.244",
                u"proto": u"ICMP",
                u"timestamp": 1446146494,
                u"dup": 0,
                u"type": u"ping",
                u"sent": 3,
                u"msm_id": 2882184,
                u"fw": 4720,
                u"max": 218.077484,
                u"step": 240,
                u"src_addr": u"10.30.0.4",
                u"rcvd": 3,
                u"msm_name": u"Ping",
                u"lts": 70,
                u"dst_name": u"194.88.241.228",
                u"min": 36.921608,
                u"group_id": 2882184,
                u"dst_addr": u"194.88.241.228",
            },
        ]
        cls.sagans = [
            Result.get(
                result, on_error=Result.ACTION_IGNORE, on_warning=Result.ACTION_IGNORE
            )
            for result in cls.results
        ]

    def test_footer(self):
        """Tests whole functionality of footer unit."""
        expected_output = (
            "\n"
            "--- 194.88.241.228 ping statistics ---\n"
            "15 packets transmitted, 15 received, 0.0% loss\n"
            "rtt min/med/avg/max = 36.922/42.406/82.693/218.077 ms\n"
        )

        r = Renderer()
        for s in self.sagans:
            r.on_result(s)

        self.assertEqual(r.footer(), expected_output)

    def test_collect_stats(self):
        """Tests collect stats function."""

        renderer = Renderer()
        for s in self.sagans:
            renderer.collect_stats(s)
        self.assertEqual(
            renderer.rtts,
            [
                42.343,
                42.22,
                42.406,
                76.611,
                76.39,
                76.474,
                154.118,
                154.197,
                154.845,
                42.264,
                42.196,
                42.343,
                218.077,
                36.922,
                38.994,
            ],
        )
        self.assertEqual(renderer.target, "194.88.241.228")
        self.assertEqual(renderer.sent_packets, 15)
        self.assertEqual(renderer.received_packets, 15)
        self.assertEqual(
            renderer.rtts_min, [42.220215, 76.38997, 154.118, 42.196233, 36.921608]
        )
        self.assertEqual(
            renderer.rtts_max, [42.40614, 76.61127, 154.845, 42.342921, 218.077484]
        )

    def test_collect_min_max_rtts(self):
        """Test use cases for collecting min max rtts."""
        renderer = Renderer()
        renderer.collect_min_max_rtts("min", 3)
        self.assertEqual(renderer.rtts_min, [3])
        renderer.collect_min_max_rtts("min", None)
        self.assertEqual(renderer.rtts_min, [3, 0])

        renderer.collect_min_max_rtts("max", 3)
        self.assertEqual(renderer.rtts_max, [3])
        renderer.collect_min_max_rtts("max", None)
        self.assertEqual(renderer.rtts_max, [3, 0])

    def test_collect_packets_rtt(self):
        """Test use cases for collecting rtts."""
        Packet = namedtuple("Packet", "rtt")
        packets = [Packet(rtt=2), Packet(rtt=3.2), Packet(rtt=5.0)]
        renderer = Renderer()
        renderer.collect_packets_rtt(packets)
        self.assertEqual(renderer.rtts, [2, 3.2, 5.0])

        packets = [Packet(rtt=None), Packet(rtt=3.2), Packet(rtt=5.0)]
        renderer = Renderer()
        renderer.collect_packets_rtt(packets)
        self.assertEqual(renderer.rtts, [0, 3.2, 5.0])

    def test_calculate_loss(self):
        """Test use cases for calculating loss."""
        renderer = Renderer()
        renderer.sent_packets = 10
        renderer.received_packets = 9
        self.assertEqual(renderer.calculate_loss(), 9.999999999999998)
        renderer.sent_packets = 0
        self.assertEqual(renderer.calculate_loss(), 0)
        renderer.received_packets = 0
        renderer.sent_packets = 10
        self.assertEqual(renderer.calculate_loss(), 100)
        renderer.received_packets = 5
        self.assertEqual(renderer.calculate_loss(), 50)

    def test_mean(self):
        """Test use cases for calculating mean."""
        renderer = Renderer()
        renderer.rtts = [0, 2.0, 5.0, 20]
        self.assertEqual(renderer.mean(), 6.75)
        renderer.rtts = [0, 2.0, 7.5, 5.0, 20]
        self.assertEqual(renderer.mean(), 6.9)
        renderer.rtts = [0, 2.0, 7.5, 5.0, 20, 50]
        self.assertEqual(renderer.mean(), 14.083)

    def test_median(self):
        """Test use cases for calculating median."""
        renderer = Renderer()
        renderer.rtts = [0, 2.0, 5.0, 20]
        self.assertEqual(renderer.median(), 3.5)
        renderer.rtts = [0, 2.0, 7.5, 5.0, 20]
        self.assertEqual(renderer.median(), 5)
        renderer.rtts = [0, 2.0, 7.5, 5.0, 20, 50]
        self.assertEqual(renderer.median(), 6.25)
