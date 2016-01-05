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

from ripe.atlas.sagan import Result
from ripe.atlas.tools.renderers.ping import Renderer


class TestPingRenderer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.basic = Result.get('{"af":4,"prb_id":1,"result":[{"rtt":10.001},{"rtt":10.002},{"rtt":10.003}],"ttl":20,"avg":10.002,"size":20,"from":"1.2.3.4","proto":"ICMP","timestamp":1440000000,"dup":0,"type":"ping","sent":3,"msm_id":1000001,"fw":4700,"max":10.003,"step":360,"src_addr":"2.3.4.5","rcvd":3,"msm_name":"Ping","lts":40,"dst_name":"my.name.ca","min":10.001,"dst_addr":"3.4.5.6"}')
        self.no_packets = Result.get('{"af":4,"prb_id":2,"result":[],"ttl":20,"avg":10.002,"size":20,"from":"1.2.3.4","proto":"ICMP","timestamp":1440000000,"dup":0,"type":"ping","sent":3,"msm_id":1000001,"fw":4700,"max":null,"step":360,"src_addr":"2.3.4.5","rcvd":0,"msm_name":"Ping","lts":40,"dst_name":"my.name.ca","min":null,"dst_addr":"3.4.5.6"}')

    def test_basic(self):
        self.assertEqual(
            Renderer().on_result(self.basic),
            "20 bytes from probe #1     1.2.3.4         to my.name.ca (3.4.5.6): ttl=20 times:10.001,  10.002,  10.003, \n"
        )

    def test_no_packets(self):
        self.assertEqual(
            Renderer().on_result(self.no_packets), "No packets found\n")
