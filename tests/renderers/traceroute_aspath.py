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

from argparse import Namespace
import json
import unittest

from ripe.atlas.sagan import Result
from ripe.atlas.tools.renderers.traceroute_aspath import Renderer


class TestTracerouteASPathRenderer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.results = json.loads('[{"af":4,"dst_addr":"194.0.25.10","dst_name":"194.0.25.10","endtime":1457447366,"from":"24.130.240.251","fw":4730,"group_id":3606560,"lts":115,"msm_id":3606560,"msm_name":"Traceroute","prb_id":12185,"proto":"ICMP","result":[{"hop":1,"result":[{"from":"192.168.2.254","rtt":0.527,"size":76,"ttl":64},{"from":"192.168.2.254","rtt":0.373,"size":76,"ttl":64},{"from":"192.168.2.254","rtt":0.325,"size":76,"ttl":64}]},{"hop":2,"result":[{"from":"96.120.89.13","ittl":0,"rtt":8.723,"size":28,"ttl":63},{"from":"96.120.89.13","ittl":0,"rtt":8.74,"size":28,"ttl":63},{"from":"96.120.89.13","ittl":0,"rtt":8.899,"size":28,"ttl":63}]},{"hop":3,"result":[{"from":"68.87.198.29","rtt":9.573,"size":68,"ttl":253},{"from":"68.87.198.29","rtt":8.938,"size":68,"ttl":253},{"from":"68.87.198.29","rtt":10.441,"size":68,"ttl":253}]},{"hop":4,"result":[{"from":"162.151.79.133","rtt":10.924,"size":68,"ttl":252},{"from":"162.151.79.133","rtt":11.039,"size":68,"ttl":252},{"from":"162.151.79.133","rtt":11.313,"size":68,"ttl":252}]},{"hop":5,"result":[{"from":"68.85.154.93","rtt":12.945,"size":68,"ttl":251},{"from":"68.85.154.93","rtt":11.193,"size":68,"ttl":251},{"from":"68.85.154.93","rtt":11.968,"size":68,"ttl":251}]},{"hop":6,"result":[{"from":"4.68.127.109","rtt":11.842,"size":76,"ttl":59},{"from":"4.68.127.109","rtt":12.573,"size":76,"ttl":59},{"from":"4.68.127.109","rtt":19.752,"size":76,"ttl":59}]},{"hop":7,"result":[{"from":"4.69.144.143","rtt":19.838,"size":28,"ttl":245},{"from":"4.69.144.143","rtt":19.709,"size":28,"ttl":245},{"from":"4.69.144.143","rtt":19.818,"size":28,"ttl":245}]},{"hop":8,"result":[{"from":"4.69.144.143","rtt":19.703,"size":28,"ttl":245},{"from":"4.69.144.143","rtt":20.591,"size":28,"ttl":245},{"from":"4.69.144.143","rtt":18.912,"size":28,"ttl":245}]},{"hop":9,"result":[{"from":"64.215.81.146","rtt":19.955,"size":28,"ttl":245},{"from":"64.215.81.146","rtt":19.629,"size":28,"ttl":245},{"from":"64.215.81.146","rtt":20.386,"size":28,"ttl":245}]},{"hop":10,"result":[{"from":"202.147.51.46","rtt":21.059,"size":28,"ttl":245},{"from":"202.147.51.46","rtt":24.6,"size":28,"ttl":245},{"from":"202.147.51.46","rtt":26.703,"size":28,"ttl":245}]},{"hop":11,"result":[{"from":"194.0.25.10","rtt":21.819,"size":48,"ttl":54},{"from":"194.0.25.10","rtt":20.215,"size":48,"ttl":54},{"from":"194.0.25.10","rtt":19.047,"size":48,"ttl":54}]}],"size":48,"src_addr":"192.168.2.91","timestamp":1457447365,"type":"traceroute"},{"af":4,"dst_addr":"194.0.25.10","dst_name":"194.0.25.10","endtime":1457447366,"from":"204.14.101.2","fw":4730,"group_id":3606560,"lts":25,"msm_id":3606560,"msm_name":"Traceroute","prb_id":22880,"proto":"ICMP","result":[{"hop":1,"result":[{"from":"192.168.1.1","rtt":0.824,"size":76,"ttl":64},{"from":"192.168.1.1","rtt":0.406,"size":76,"ttl":64},{"from":"192.168.1.1","rtt":0.359,"size":76,"ttl":64}]},{"hop":2,"result":[{"from":"192.168.2.254","rtt":0.547,"size":28,"ttl":63},{"from":"192.168.2.254","rtt":0.451,"size":28,"ttl":63},{"from":"192.168.2.254","rtt":0.454,"size":28,"ttl":63}]},{"hop":3,"result":[{"from":"10.32.128.1","rtt":12.876,"size":28,"ttl":253},{"from":"10.32.128.1","rtt":9.85,"size":28,"ttl":253},{"from":"10.32.128.1","rtt":9.656,"size":28,"ttl":253}]},{"hop":4,"result":[{"from":"10.32.255.1","rtt":10.112,"size":28,"ttl":61},{"from":"10.32.255.1","rtt":8.231,"size":28,"ttl":61},{"from":"10.32.255.1","rtt":14.477,"size":28,"ttl":61}]},{"hop":5,"result":[{"from":"204.14.96.221","rtt":11.434,"size":28,"ttl":251},{"from":"204.14.96.221","rtt":9.149,"size":28,"ttl":251},{"from":"204.14.96.221","rtt":11.625,"size":28,"ttl":251}]},{"hop":6,"result":[{"from":"204.106.235.2","rtt":11.714,"size":28,"ttl":250},{"from":"204.106.235.2","rtt":13.193,"size":28,"ttl":250},{"from":"204.106.235.2","rtt":16.916,"size":28,"ttl":250}]},{"hop":7,"result":[{"from":"206.81.80.40","rtt":15.283,"size":28,"ttl":58},{"from":"206.81.80.40","rtt":28.69,"size":28,"ttl":58},{"from":"206.81.80.40","rtt":27.795,"size":28,"ttl":58}]},{"hop":8,"result":[{"from":"72.52.92.157","rtt":33.901,"size":28,"ttl":57},{"from":"72.52.92.157","rtt":41.775,"size":28,"ttl":57},{"from":"72.52.92.157","rtt":38.496,"size":28,"ttl":57}]},{"hop":9,"result":[{"from":"216.218.192.234","rtt":31.631,"size":68,"ttl":238},{"from":"216.218.192.234","rtt":30.064,"size":68,"ttl":238},{"from":"216.218.192.234","rtt":29.304,"size":68,"ttl":238}]},{"hop":10,"result":[{"from":"202.147.61.206","rtt":40.974,"size":68,"ttl":238},{"from":"202.147.61.206","rtt":39.599,"size":68,"ttl":238},{"from":"202.147.61.206","rtt":40.409,"size":68,"ttl":238}]},{"hop":11,"result":[{"from":"202.147.58.142","rtt":41.353,"size":28,"ttl":238},{"from":"202.147.58.142","rtt":40.937,"size":28,"ttl":238},{"from":"202.147.58.142","rtt":39.937,"size":28,"ttl":238}]},{"hop":12,"result":[{"from":"202.147.51.46","rtt":41.58,"size":28,"ttl":237},{"from":"202.147.51.46","rtt":45.443,"size":28,"ttl":237},{"from":"202.147.51.46","rtt":41.242,"size":28,"ttl":237}]},{"hop":13,"result":[{"from":"194.0.25.10","rtt":41.256,"size":48,"ttl":45},{"from":"194.0.25.10","rtt":40.092,"size":48,"ttl":45},{"from":"194.0.25.10","rtt":40.657,"size":48,"ttl":45}]}],"size":48,"src_addr":"192.168.1.4","timestamp":1457447365,"type":"traceroute"}]')

    def run_renderer(self, traceroute_aspath_radius=2):
        args = Namespace(traceroute_aspath_radius=traceroute_aspath_radius)
        renderer = Renderer(arguments=args)
        output = ""
        for res in self.results:
            output += renderer.on_result(Result.get(res))
        output += renderer.additional(None)
        return output

    def test_basic(self):
        output = self.run_renderer()
        expected = """Probe #12185:  AS10026   AS1921, completed
Probe #22880:  AS10026   AS1921, completed

Number of probes for each AS path:

   AS10026   AS1921: 2 probes, 2 completed
"""
        self.assertEqual(output, expected)

    def test_arg_radius(self):
        output = self.run_renderer(traceroute_aspath_radius=4)
        expected = """Probe #12185:   AS3356   AS3549  AS10026   AS1921, completed
Probe #22880:  AS26088   AS6939  AS10026   AS1921, completed

Number of probes for each AS path:

   AS26088   AS6939  AS10026   AS1921: 1 probe, 1 completed
    AS3356   AS3549  AS10026   AS1921: 1 probe, 1 completed
"""
        self.assertEqual(output, expected)
