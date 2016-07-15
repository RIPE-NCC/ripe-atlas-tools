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
import requests

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

from ripe.atlas.tools.commands.probe_search import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.cousteau import Probe
from ripe.atlas.tools.aggregators import ValueKeyAggregator

from ..base import capture_sys_output


COMMAND_MODULE = "ripe.atlas.tools.commands.probe_search"


class FakeGen(object):
    def __init__(self,):
        self.probes = [
            Probe(id=1, meta_data={
                "country_code": "GR", "asn_v4": 3333, "prefix_v4": "193.0/22"}),
            Probe(id=2, meta_data={
                "country_code": "DE", "asn_v4": 3333, "prefix_v4": "193.0/22"}),
            Probe(id=3, meta_data={
                "country_code": "DE", "asn_v4": 3332, "prefix_v4": "193.0/22"}),
            Probe(id=4, meta_data={
                "country_code": "NL", "asn_v4": 3333, "prefix_v4": "193.0/22"}),
            Probe(id=5, meta_data={
                "country_code": "GR", "asn_v4": 3333, "prefix_v4": "193.0/22"}),
        ]
        self.total_count = 4

    def __iter__(self):
        return self

    # Python 3 compatibility
    def __next__(self):
        return self.next()

    def next(self):
        if not self.probes:
            raise StopIteration()
        else:
            return self.probes.pop(0)


class TestProbesCommand(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_with_empty_args(self):
        """User passes no args, should fail with RipeAtlasToolsException"""
        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args([])
            cmd.run()

    def test_with_random_args(self):
        """User passes random args, should fail with SystemExit"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["blaaaaaaa"])
                cmd.run()

    def test_arg_with_no_value(self):
        """User passed not boolean arg but no value"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--asn"])
                cmd.run()

    def test_arg_with_wrong_type(self):
        """User passed arg with wrong type. e.g string for asn"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--asn", "blaaaaa"])
                cmd.run()
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--asnv4", "blaaaaa"])
                cmd.run()
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--asnv6", "blaaaaa"])
                cmd.run()
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--limit", "blaaaaa"])
                cmd.run()
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--radius", "blaaaaa"])
                cmd.run()
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--tag", "inv@lid"])
                cmd.run()

    def test_location_google_breaks(self):
        """User passed location arg but google api gave error"""
        caught_exceptions = [
            requests.ConnectionError, requests.HTTPError, requests.Timeout]
        with mock.patch('requests.get') as mock_get:
            for exception in caught_exceptions:
                mock_get.side_effect = exception
                with capture_sys_output():
                    with self.assertRaises(RipeAtlasToolsException):
                        cmd = Command()
                        cmd.init_args(["--location", "blaaaa"])
                        cmd.run()
            mock_get.side_effect = Exception()
            with self.assertRaises(Exception):
                cmd = Command()
                cmd.init_args(["--location", "blaaaa"])
                cmd.run()

    def test_location_google_wrong_output(self):
        """User passed location arg but google api gave not expected format"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"blaaa": "bla"}
                with self.assertRaises(RipeAtlasToolsException):
                    cmd = Command()
                    cmd.init_args(["--location", "blaaaa"])
                    cmd.run()

    def test_location_arg(self):
        """User passed location arg"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"results": [
                    {"geometry": {"location": {"lat": 1, "lng": 2}}}]}
                cmd = Command()
                cmd.init_args(["--location", "blaaaa"])
                self.assertEquals(cmd.build_request_args(), {'radius': '1,2:15'})

    def test_location_arg_with_radius(self):
        """User passed location arg"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"results": [
                    {"geometry": {"location": {"lat": 1, "lng": 2}}}
                ]}
                cmd = Command()
                cmd.init_args(["--location", "blaaaa", "--radius", "4"])
                self.assertEquals(
                    cmd.build_request_args(),
                    {"radius": "1,2:4"}
                )

    def test_asn_args(self):
        """User passed asn arg together with asnv4 or asnv6"""
        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args(["--asn", "3333", "--asnv4", "3333"])
            cmd.run()

        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args(["--asn", "3333", "--asnv6", "3333"])
            cmd.run()

    def test_prefix_args(self):
        """User passed prefix arg together with prefixv4 or prefixv6"""
        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args([
                "--prefix", "193.0.0.0/21",
                "--prefixv4", "193.0.0.0/21"
            ])
            cmd.run()

        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args([
                "--prefix", "2001:67c:2e8::/48",
                "--prefixv6", "2001:67c:2e8::/48"
            ])
            cmd.run()

    def test_all_args(self):
        """User passed all arguments"""
        cmd = Command()
        cmd.init_args(["--all"])
        self.assertEquals(cmd.build_request_args(), {})

    def test_center_arg_wrong_value(self):
        """User passed center arg with wrong value"""
        with self.assertRaises(RipeAtlasToolsException):
            cmd = Command()
            cmd.init_args(["--center", "blaaaa"])
            cmd.run()

    def test_center_arg(self):
        """User passed center arg"""
        cmd = Command()
        cmd.init_args(["--center", "1,2"])
        self.assertEquals(
            cmd.build_request_args(),
            {"radius": "1,2:15"}
        )

    def test_center_arg_with_radius(self):
        """User passed center and radius arg"""
        cmd = Command()
        cmd.init_args(["--center", "1,2", "--radius", "4"])
        self.assertEquals(cmd.build_request_args(), {"radius": "1,2:4"})

    def test_country_arg(self):
        """User passed country code arg"""
        cmd = Command()
        cmd.init_args(["--country", "GR"])
        self.assertEquals(cmd.build_request_args(), {"country_code": "GR"})

    def test_country_arg_with_radius(self):
        """User passed country code arg together with radius"""
        cmd = Command()
        cmd.init_args(["--country", "GR", "--radius", "4"])
        self.assertEquals(cmd.build_request_args(), {"country_code": "GR"})

    def test_status_arg(self):
        """User passed valid status arg."""
        for status in range(0, 3):
            cmd = Command()
            cmd.init_args(["--status", str(status)])
            self.assertEquals(cmd.build_request_args(), {"status": status})

    def test_status_arg_wrong_value(self):
        """User passed status arg with wrong value"""
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                cmd = Command()
                cmd.init_args(["--status", "4"])
                cmd.run()

    def test_sane_tags(self):
        """Sane tags"""
        cmd = Command()
        cmd.init_args(["--tag", "native-ipv6"])
        self.assertEquals(
            cmd.build_request_args(),
            {"tags": "native-ipv6"}
        )

        cmd = Command()
        cmd.init_args(["--tag", "native-ipv6", "--tag", "system-ipv4-works"])
        self.assertEquals(
            cmd.build_request_args(),
            {"tags": "native-ipv6,system-ipv4-works"}
        )

    def test_sane_args1(self):
        """User passed several arguments (1)"""
        cmd = Command()
        cmd.init_args([
            "--center", "1,2",
            "--radius", "4",
            "--asnv4", "3333",
            "--prefix", "193.0.0.0/21"
        ])
        self.assertEquals(
            cmd.build_request_args(),
            {'asn_v4': 3333, 'prefix': '193.0.0.0/21', 'radius': '1,2:4'}
        )

    def test_sane_args2(self):
        """User passed several arguments (2)"""

        cmd = Command()
        cmd.init_args([
            "--location", "Amsterdam",
            "--asn", "3333",
            "--prefixv4", "193.0.0.0/21"
        ])

        path = '{}.Command.location2degrees'.format(COMMAND_MODULE)
        with mock.patch(path) as mock_get:
            mock_get.return_value = (1, 2)
            self.assertEquals(cmd.build_request_args(), {
                'asn': 3333,
                'prefix_v4': '193.0.0.0/21',
                'radius': '1,2:15'
            })

    def test_sane_args3(self):
        """User passed several arguments (3)"""

        cmd = Command()
        cmd.init_args([
            "--center", "1,2",
            "--asnv6", "3333",
            "--prefixv6", "2001:67c:2e8::/48"
        ])
        self.assertEquals(cmd.build_request_args(), {
            'asn_v6': 3333,
            'prefix_v6': '2001:67c:2e8::/48',
            'radius': '1,2:15'
        })

    def test_render_ids_only(self):
        """User passed ids_only arg, testing rendiring"""

        cmd = Command()
        cmd.init_args([
            "--ids-only", "--country", "GR"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                self.assertEquals(stdout.getvalue(), "1\n2\n3\n4\n5\n")

    def test_render_ids_only_with_limit(self):
        """User passed ids_only arg together with limit, testing rendering"""
        cmd = Command()
        cmd.init_args([
            "--ids-only",
            "--country", "GR",
            "--limit", "2"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                self.assertEquals(stdout.getvalue(), "1\n2\n")

    def test_render_ids_only_with_aggr(self):
        """
        User passed ids_only arg together with aggregate, testing rendering
        """
        cmd = Command()
        cmd.init_args([
            "--ids-only",
            "--country", "GR",
            "--aggregate-by", "country"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                self.assertEquals(stdout.getvalue(), "1\n2\n3\n4\n5\n")

    def test_get_aggregators(self):
        """User passed --aggregate-by args"""
        cmd = Command()
        cmd.init_args([
            "--aggregate-by", "asn_v4",
            "--aggregate-by", "country",
            "--aggregate-by", "prefix_v4"
        ])
        expected_output = [
            ValueKeyAggregator(key="asn_v4"),
            ValueKeyAggregator(key="country_code"),
            ValueKeyAggregator(key="prefix_v4")
        ]
        cmd.set_aggregators()
        for index, v in enumerate(cmd.aggregators):
            self.assertTrue(isinstance(v, ValueKeyAggregator))
            self.assertEquals(
                v.aggregation_keys,
                expected_output[index].aggregation_keys
            )

    def test_render_without_aggregation(self):
        """Tests rendering of results without aggregation"""
        cmd = Command()
        cmd.init_args([
            "--country", "GR"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                expected_output = (
                    "\n"
                    "Filters:\n"
                    "  Country: GR\n"
                    "\n"
                    "ID    Asn_v4 Asn_v6 Country Status         \n"
                    "===========================================\n"
                    "1     3333            gr    None           \n"
                    "2     3333            de    None           \n"
                    "3     3332            de    None           \n"
                    "4     3333            nl    None           \n"
                    "5     3333            gr    None           \n"
                    "===========================================\n"
                    "                Showing 4 of 4 total probes\n"
                    "\n"
                )
                self.assertEquals(stdout.getvalue(), expected_output)

    def test_render_without_aggregation_with_limit(self):
        """Tests rendering of results without aggregation but with limit"""
        cmd = Command()
        cmd.init_args([
            "--country", "GR",
            "--limit", "2"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = 'ripe.atlas.tools.commands.probe_search.ProbeRequest'
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                expected_output = (
                    "\n"
                    "Filters:\n"
                    "  Country: GR\n"
                    "\n"
                    "ID    Asn_v4 Asn_v6 Country Status         \n"
                    "===========================================\n"
                    "1     3333            gr    None           \n"
                    "2     3333            de    None           \n"
                    "===========================================\n"
                    "                Showing 2 of 4 total probes\n"
                    "\n"
                )
                self.assertEquals(stdout.getvalue(), expected_output)

    def test_render_with_aggregation(self):
        """Tests rendering of results with aggregation"""
        cmd = Command()
        cmd.init_args([
            "--country", "GR",
            "--aggregate-by", "country",
            "--aggregate-by", "asn_v4",
            "--aggregate-by", "prefix_v4"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                expected_blob = (
                    "\n"
                    "Filters:\n"
                    "  Country: GR\n"
                    "\n"
                    "   ID    Asn_v4 Asn_v6 Country Status         \n"
                    "==============================================\n"
                    "Country: DE\n"
                    " ASN_V4: 3332\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   3     3332            de    None           \n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   2     3333            de    None           \n"
                    "\n"
                    "Country: GR\n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   1     3333            gr    None           \n"
                    "   5     3333            gr    None           \n"
                    "\n"
                    "Country: NL\n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   4     3333            nl    None           \n"
                    "==============================================\n"
                    "                   Showing 4 of 4 total probes\n"
                    "\n"
                )
                expected_set = set(expected_blob.split("\n"))
                returned_set = set(stdout.getvalue().split("\n"))
                self.assertEquals(returned_set, expected_set)

    def test_render_with_aggregation_with_limit(self):
        """Tests rendering of results with aggregation with limit"""
        cmd = Command()
        cmd.init_args([
            "--country", "GR",
            "--aggregate-by", "country",
            "--aggregate-by", "asn_v4",
            "--aggregate-by", "prefix_v4",
            "--limit", "1"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                expected_output = (
                    "\n"
                    "Filters:\n"
                    "  Country: GR\n"
                    "\n"
                    "   ID    Asn_v4 Asn_v6 Country Status         \n"
                    "==============================================\n"
                    "Country: GR\n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   1     3333            gr    None           \n"
                    "==============================================\n"
                    "                   Showing 1 of 4 total probes\n"
                    "\n"
                )
                expected_set = set(expected_output.split("\n"))
                returned_set = set(stdout.getvalue().split("\n"))
                self.assertEquals(returned_set, expected_set)

    def test_render_with_aggregation_with_max_per_aggr(self):
        """
        Tests rendering of results with aggregation with max per aggr option
        """
        cmd = Command()
        cmd.init_args([
            "--country", "GR",
            "--aggregate-by", "country",
            "--aggregate-by", "asn_v4",
            "--aggregate-by", "prefix_v4",
            "--max-per-aggregation", "1"
        ])

        with capture_sys_output() as (stdout, stderr):
            path = '{}.ProbeRequest'.format(COMMAND_MODULE)
            with mock.patch(path) as mock_get:
                mock_get.return_value = FakeGen()
                cmd.run()
                expected_output = (
                    "\n"
                    "Filters:\n  "
                    "Country: GR\n"
                    "\n"
                    "   ID    Asn_v4 Asn_v6 Country Status         \n"
                    "==============================================\n"
                    "Country: DE\n"
                    " ASN_V4: 3332\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   3     3332            de    None           \n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   2     3333            de    None           \n"
                    "\n"
                    "Country: GR\n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   1     3333            gr    None           \n"
                    "\n"
                    "Country: NL\n"
                    " ASN_V4: 3333\n"
                    "  PREFIX_V4: 193.0/22\n"
                    "   4     3333            nl    None           \n"
                    "==============================================\n"
                    "                   Showing 4 of 4 total probes\n"
                    "\n"
                )
                expected_set = set(expected_output.split("\n"))
                returned_set = set(stdout.getvalue().split("\n"))
                self.assertEquals(returned_set, expected_set)
