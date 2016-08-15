# coding=utf-8

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

import copy
import json
import os
import sys
import tempfile
import unittest

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

from ripe.atlas.cousteau import Probe

from ripe.atlas.tools.commands.report import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.tools.renderers import Renderer
from ripe.atlas.tools.settings import AliasesDB
from ripe.atlas.tools.version import __version__
from ..base import capture_sys_output, StringIO


class TestReportCommand(unittest.TestCase):

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
    expected_output_no_aggr = (
        "20 bytes from probe #1216  109.190.83.40   to hsi.cablecom.ch (62.2.16.24): ttl=54 times:27.429,  25.672,  25.681, \n"
        "20 bytes from probe #165   194.85.27.7     to hsi.cablecom.ch (62.2.16.24): ttl=48 times:87.825,  87.611,  91.0,   \n"
        "20 bytes from probe #202   178.190.51.206  to hsi.cablecom.ch (62.2.16.24): ttl=52 times:40.024,  40.399,  39.29,  \n"
        "20 bytes from probe #2225  46.126.90.165   to hsi.cablecom.ch (62.2.16.24): ttl=56 times:10.858,  12.632,  20.53,   32.775,  47.509,  62.745,  78.54,   93.272,  109.738,\n"
        "20 bytes from probe #270   188.192.110.111 to hsi.cablecom.ch (62.2.16.24): ttl=51 times:28.527,  26.586,  26.393, \n"
        "20 bytes from probe #579   195.88.195.170  to hsi.cablecom.ch (62.2.16.24): ttl=51 times:23.201,  22.981,  22.863, \n"
        "20 bytes from probe #677   78.128.9.202    to hsi.cablecom.ch (62.2.16.24): ttl=54 times:40.715,  40.259,  40.317, \n"
        "20 bytes from probe #879   94.254.125.2    to hsi.cablecom.ch (62.2.16.24): ttl=53 times:34.32,   34.446,  34.376, \n"
        "20 bytes from probe #945   92.111.237.94   to hsi.cablecom.ch (62.2.16.24): ttl=56 times:61.665,  23.833,  23.269, \n"
    )

    def setUp(self):
        self.cmd = Command()

    def test_with_empty_args(self):
        """User passes no args, should fail with SystemExit"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args([])
                self.cmd.run()

    def test_with_random_args(self):
        """User passes random args, should fail with SystemExit"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["blaaaaaaa"])
                self.cmd.run()

    def test_arg_with_no_value(self):
        """User passed not boolean arg but no value"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["--probes"])
                self.cmd.run()

    def test_arg_with_wrong_type(self):
        """User passed arg with wrong type."""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["--probes", "blaaaaa"])
                self.cmd.run()

    def test_arg_renderer_with_wrong_choice(self):
        """User passed arg renderer with unavailable type."""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["--renderer", "blaaaaa"])
                self.cmd.run()

    def test_arg_renderer_with_valid_choice(self):
        """User passed arg renderer with valid type."""
        # Mock AtlasRequest to fail run fast and test args validity.
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.return_value = False, {}
            for choice in Renderer.get_available():
                with self.assertRaises(RipeAtlasToolsException):
                    cmd = Command()
                    cmd.init_args(["--renderer", choice, "1"])
                    cmd.run()

    def test_arg_renderer_traceroute_aspath_with_valid_radius_arg(self):
        """User passed arg --traceroute-aspath-radius to traceroute_aspath renderer"""
        # Mock AtlasRequest to fail run fast and test args validity.
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.return_value = False, {}
            with self.assertRaises(RipeAtlasToolsException):
                cmd = Command()
                cmd.init_args(["--renderer", "traceroute_aspath",
                               "--traceroute-aspath-radius", "3",
                               "1"])
                cmd.run()

    def test_arg_renderer_traceroute_aspath_with_invalid_radius_arg(self):
        """User passed arg --traceroute-aspath-radius to traceroute_aspath renderer with invalid value"""
        # Mock AtlasRequest to fail run fast and test args validity.
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--renderer", "traceroute_aspath",
                               "--traceroute-aspath-radius", "blaaaaa",
                               "1"])
                cmd.run()

    def test_arg_aggregate_with_valid_choice(self):
        """User passed arg aggregate with valid type."""
        # Mock AtlasRequest to fail run fast and test args validity.
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.return_value = False, {}
            for choice in Command.AGGREGATORS.keys():
                with self.assertRaises(RipeAtlasToolsException):
                    cmd = Command()
                    cmd.init_args(["--aggregate-by", choice, "1"])
                    cmd.run()

    def test_arg_aggregate_with_wrong_choice(self):
        """User passed arg aggregate with unavailable type."""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["--aggregate-by", "blaaaaa"])
                self.cmd.run()

    def test_arg_no_source(self):
        """User passed no measurement id and no file name."""
        with capture_sys_output(use_fake_tty=True):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["--aggregate-by", "country"])
                self.cmd.run()

    def test_arg_from_file(self):
        """User passed a valid filename"""
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        try:
            temp_file.write(
                json.dumps(self.mocked_results).encode("utf-8")
            )
            temp_file.close()
            with capture_sys_output() as (stdout, stderr):
                self.cmd.init_args([
                    "--from-file", temp_file.name,
                ])
                self.cmd.run()
                assert self.expected_output_no_aggr == stdout.getvalue()
        finally:
            os.unlink(temp_file.name)

    def test_arg_from_stdin(self):
        """User passes results into standard input"""
        try:
            current_stdin = sys.stdin
            sys.stdin = StringIO(json.dumps(self.mocked_results))
            with capture_sys_output() as (stdout, stderr):
                self.cmd.init_args([])
                self.cmd.run()
                assert self.expected_output_no_aggr == stdout.getvalue()
        finally:
            sys.stdin = current_stdin

    def test_arg_no_valid_msm_id(self):
        """User passed non valid type of measurement id."""
        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["blaaa"])
                self.cmd.run()
            err = stderr.getvalue().split("\n")[-2]
        self.assertEqual(
            err,
            'ripe-atlas report: error: argument measurement_id: "blaaa" '
            'does not appear to be an existent measurement alias.'
        )

    def test_arg_valid_msm_alias(self):
        """User passed a valid measurement alias."""
        path_aliases = "ripe.atlas.tools.helpers.validators.aliases"
        new_aliases = copy.deepcopy(AliasesDB.DEFAULT)
        new_aliases['measurement']['UNITTEST_ALIAS'] = 1234
        with mock.patch(path_aliases, new_aliases):
            path_get = 'ripe.atlas.tools.commands.report.Command._get_results_from_api'
            with mock.patch(path_get) as mock_get:
                mock_get.side_effect = RipeAtlasToolsException
                with self.assertRaises(RipeAtlasToolsException):
                    self.cmd.init_args(["UNITTEST_ALIAS"])
                    self.cmd.run()
                mock_get.assert_called_once_with(1234)

    def test_measurement_failure(self):
        """Testcase where given measurement id doesn't exist."""
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.return_value = False, {}
            with self.assertRaises(RipeAtlasToolsException):
                self.cmd.init_args(["--aggregate-by", "country", "1"])
                self.cmd.run()

    def test_no_results(self):
        """Testcase where given measurement id doesn't have any results."""
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.side_effect = [
                (True, {})
            ]
            with self.assertRaises(RipeAtlasToolsException):
                self.cmd.init_args(["--aggregate-by", "country", "1"])
                self.cmd.run()

    def test_no_renderer_found(self):
        """Testcase where renderer canoot be founbd from measurement type."""
        path = 'ripe.atlas.cousteau.AtlasRequest.get'
        with mock.patch(path) as mock_get:
            mock_get.side_effect = [
                (True, {})
            ]
            with self.assertRaises(RipeAtlasToolsException):
                self.cmd.init_args(["--aggregate-by", "country", "1"])
                self.cmd.run()

    def test_valid_case_no_aggr(self):
        """Test case where we have result no aggregation."""
        probes = [
            Probe(id=202, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=677, meta_data={
                "country_code": "DE", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=2225, meta_data={
                "country_code": "DE", "asn_v4": 3332, "asn_v6": "4444"}),
            Probe(id=165, meta_data={
                "country_code": "NL", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=1216, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=270, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=579, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=945, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
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
                    self.cmd.init_args(["1"])
                    self.cmd.run()
                    self.assertEquals(
                        stdout.getvalue(), self.expected_output_no_aggr
                    )

    def test_valid_case_with_aggr(self):
        """Test case where we have result with aggregation."""
        expected_output = (
            "RTT_MEDIAN: 40-50\n"
            " 20 bytes from probe #202   178.190.51.206  to hsi.cablecom.ch (62.2.16.24): ttl=52 times:40.024,  40.399,  39.29,  \n"
            " 20 bytes from probe #677   78.128.9.202    to hsi.cablecom.ch (62.2.16.24): ttl=54 times:40.715,  40.259,  40.317, \n"
            "RTT_MEDIAN: 10-20\n"
            " 20 bytes from probe #2225  46.126.90.165   to hsi.cablecom.ch (62.2.16.24): ttl=56 times:10.858,  12.632,  20.53,   32.775,  47.509,  62.745,  78.54,   93.272,  109.738,\n"
            "RTT_MEDIAN: 50-100\n"
            " 20 bytes from probe #165   194.85.27.7     to hsi.cablecom.ch (62.2.16.24): ttl=48 times:87.825,  87.611,  91.0,   \n"
            "RTT_MEDIAN: 20-30\n"
            " 20 bytes from probe #1216  109.190.83.40   to hsi.cablecom.ch (62.2.16.24): ttl=54 times:27.429,  25.672,  25.681, \n"
            " 20 bytes from probe #270   188.192.110.111 to hsi.cablecom.ch (62.2.16.24): ttl=51 times:28.527,  26.586,  26.393, \n"
            " 20 bytes from probe #579   195.88.195.170  to hsi.cablecom.ch (62.2.16.24): ttl=51 times:23.201,  22.981,  22.863, \n"
            " 20 bytes from probe #945   92.111.237.94   to hsi.cablecom.ch (62.2.16.24): ttl=56 times:61.665,  23.833,  23.269, \n"
            "RTT_MEDIAN: 30-40\n"
            " 20 bytes from probe #879   94.254.125.2    to hsi.cablecom.ch (62.2.16.24): ttl=53 times:34.32,   34.446,  34.376, \n"
        )
        probes = [
            Probe(id=202, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=677, meta_data={
                "country_code": "DE", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=2225, meta_data={
                "country_code": "DE", "asn_v4": 3332, "asn_v6": "4444"}),
            Probe(id=165, meta_data={
                "country_code": "NL", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=1216, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=270, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=579, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
            Probe(id=945, meta_data={
                "country_code": "GR", "asn_v4": 3333, "asn_v6": "4444"}),
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
                    self.cmd.init_args(["--aggregate-by", "rtt-median", "1"])
                    self.cmd.run()
                    expected_set = set(expected_output.split("\n"))
                    returned_set = set(stdout.getvalue().split("\n"))
                    self.assertEquals(returned_set, expected_set)

    def test_asns_filter(self):
        """Test case where user specified probe asns filters.."""
        expected_output = (
            "20 bytes from probe #165   194.85.27.7     to hsi.cablecom.ch (62.2.16.24): ttl=48 times:87.825,  87.611,  91.0,   \n"
            "20 bytes from probe #945   92.111.237.94   to hsi.cablecom.ch (62.2.16.24): ttl=56 times:61.665,  23.833,  23.269, \n"
        )

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
                    self.cmd.init_args(["1", "--probe-asns", "3334"])
                    self.cmd.run()
                    self.assertEquals(stdout.getvalue(), expected_output)

    def test_user_agent(self):
        standard = "RIPE Atlas Tools (Magellan) {}".format(__version__)
        tests = {
            standard: standard,
            "Some custom agent": "Some custom agent",
            "Some custom agent\nwith a second line": "Some custom agent",
            "x" * 3000: "x" * 128,
            "Πράκτορας χρήστη": "Πράκτορας χρήστη",
            "이것은 테스트 요원": "이것은 테스트 요원",
        }
        self.assertEqual(self.cmd.user_agent, standard)
        for in_string, out_string in tests.items():
            path = "ripe.atlas.tools.commands.base.open"
            content = mock.mock_open(read_data=in_string)
            with mock.patch(path, content, create=True):
                self.assertEqual(Command().user_agent, out_string)
