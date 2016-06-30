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

import json
import unittest

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

from ripe.atlas.cousteau import Probe

from ripe.atlas.tools.commands.report import Command
from ..base import capture_sys_output


class TestRawRenderer(unittest.TestCase):

    mocked_results = [
        {'af': 4, 'prb_id': 1216, 'result': [{'rtt': 27.429}, {'rtt': 25.672}, {'rtt': 25.681}], 'ttl': 54, 'avg': 26.2606666667, 'size': 20, 'from': '109.190.83.40', ' proto': 'ICMP', 'timestamp': 1445025400, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4700, 'max': 27.429, 'step': 360, 'src_addr': '192.168.103.132', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 377, 'dst_name': 'hsi.cablecom.ch', 'min': 25.672, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 165, 'result': [{'rtt': 87.824658}, {'rtt': 87.611154}, {'rtt': 90.99957}], 'ttl': 48, 'avg': 88.811794, 'size': 20, 'from': '194.85.27.7', 'proto': 'ICMP', 'timestamp': 1445025590, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 90.99957, 'step': 360, 'src_addr': '192.168.3.8', 'rcvd': 3, 'msm_name': 'Ping', ' lts': 87, 'dst_name': 'hsi.cablecom.ch', 'min': 87.611154, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 202, 'result': [{'rtt': 40.02356}, {'rtt': 40.399112}, {'rtt': 39.29012}], 'ttl': 52, 'avg': 39.904264, 'size': 20, 'from': '178.190.51.206', 'proto': 'ICMP', 'timestamp': 1445015502, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 40.399112, 'step': 360, 'src_addr': '10.0.0.2', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 502, 'dst_name': 'hsi.cablecom.ch', 'min': 39.29012, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 2225, 'result': [{'rtt': 10.858}, {'rtt': 12.632}, {'rtt': 20.53}, {'dup': 1, 'rtt': 32.775}, {'dup': 1, 'rtt': 47.509}, {'dup': 1, 'rtt': 62.745}, {'dup': 1, 'rtt': 78.54}, {'dup': 1, 'rtt': 93.272}, {'dup': 1, 'rtt': 109.738}], 'ttl': 56, 'avg': 14.6733333333, 'size': 20, 'from': '46.126.90.165', 'proto': 'ICMP', 'timestamp': 1445025616, 'dup': 6, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4700, 'max': 20.53, 'step': 360, 'src_addr': '192.168.111.103', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 309, 'dst_name': 'hsi.cablecom.ch', 'min': 10.858, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 270, 'result': [{'rtt': 28.527366}, {'rtt': 26.585862}, {'rtt': 26.393094}], 'ttl': 51, 'avg': 27.168774, 'size': 20, 'from': '188.192.110.111', 'proto': 'ICMP', 'timestamp': 1445025513, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 28.527366, 'step': 360, 'src_addr': '192.168.178.21', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 182, 'dst_name': 'hsi.cablecom.ch', 'min': 26.393094, 'group_id': 1000192, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 579, 'result': [{'rtt': 23.201285}, {'rtt': 22.980868}, {'rtt': 22.863364}], 'ttl': 51, 'avg': 23.0151723333, 'size': 20, 'from': '195.88.195.170', 'proto': 'ICMP', 'timestamp': 1445025521, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 23.201285, 'step': 360, 'src_addr': '10.69.8.150', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 56, 'dst_name': 'hsi.cablecom.ch', 'min': 22.863364, 'group_id': 1000192, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 677, 'result': [{'rtt': 40.71476}, {'rtt': 40.258568}, {'rtt': 40.316936}], 'ttl': 54, 'avg': 40.430088, 'size': 20, 'from': '78.128.9.202', 'proto': 'ICMP', 'timestamp': 1445025298, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 40.71476, 'step': 360, 'src_addr': '10.100.0.25', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 97, 'dst_name': 'hsi.cablecom.ch', 'min': 40.258568, 'group_id': 1000192, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 879, 'result': [{'rtt': 34.319623}, {'rtt': 34.445575}, {'rtt': 34.376455}], 'ttl': 53, 'avg': 34.380551, 'size': 20, 'from': '94.254.125.2', 'proto': 'ICMP', 'timestamp': 1445025223, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 34.445575, 'step': 360, 'src_addr': '192.168.8.130', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 189, 'dst_name': 'hsi.cablecom.ch', 'min': 34.319623, 'dst_addr': '62.2.16.24'},
        {'af': 4, 'prb_id': 945, 'result': [{'rtt': 61.665036}, {'rtt': 23.833349}, {'rtt': 23.268868}], 'ttl': 56, 'avg': 36.255751, 'size': 20, 'from': '92.111.237.94', 'proto': 'ICMP', 'timestamp': 1445025494, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4720, 'max': 61.665036, 'step': 360, 'src_addr': '92.111.237.94', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 746, 'dst_name': 'hsi.cablecom.ch', 'min': 23.268868, 'dst_addr': '62.2.16.24'}
    ]

    def setUp(self):
        self.cmd = Command()

    def test_raw_renderer(self):
        """Test case where user specified report with raw rendering."""
        json_results = []
        for result in self.mocked_results:
            json_results.append(json.dumps(result, separators=(",", ":")))
        expected_output = "\n".join(json_results) + "\n"

        probes = [
            Probe(id=202, meta_data={
                "country_code": "GR", "asn_v4": 3337, "asn_v6": "4445"}),
            Probe(id=677, meta_data={
                "country_code": "DE", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=2225, meta_data={
                "country_code": "DE", "asn_v4": 3332, "asn_v6": "4444"}),
            Probe(id=165, meta_data={
                "country_code": "NL", "asn_v4": 3334, "asn_v6": "4444"}),
            Probe(id=1216, meta_data={
                "country_code": "GR", "asn_v4": 3335, "asn_v6": "4444"}),
            Probe(id=270, meta_data={
                "country_code": "GR", "asn_v4": 3340, "asn_v6": "4444"}),
            Probe(id=579, meta_data={
                "country_code": "GR", "asn_v4": 3336, "asn_v6": "4444"}),
            Probe(id=945, meta_data={
                "country_code": "GR", "asn_v4": 3334, "asn_v6": "4444"}),
            Probe(id=879, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
        ]

        with capture_sys_output() as (stdout, stderr):
            path = 'ripe.atlas.cousteau.AtlasRequest.get'
            with mock.patch(path) as mock_get:
                mock_get.side_effect = [
                    (True, self.mocked_results)
                ]
                mpath = 'ripe.atlas.tools.helpers.rendering.Probe.get_many'
                with mock.patch(mpath) as mock_get_many:
                    mock_get_many.return_value = probes
                    self.cmd.init_args(["1", "--renderer", "raw"])
                    self.cmd.run()
                    self.assertEquals(stdout.getvalue(), expected_output)
