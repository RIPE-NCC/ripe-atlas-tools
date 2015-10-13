import sys
import mock
import unittest
import requests

try:
    from cStringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO

from ripe.atlas.tools.commands.probes import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.cousteau import Probe
from ripe.atlas.tools.aggregators import ValueKeyAggregator


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
        self.cmd = Command()

    def test_with_empty_args(self):
        """User passes no args, should fail with SystemExit"""
        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args([])
            self.cmd.run()

    def test_with_random_args(self):
        """User passes random args, should fail with SystemExit"""
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["blaaaaaaa"])
            self.cmd.run()

    def test_arg_with_no_value(self):
        """User passed not boolean arg but no value"""
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--asn"])
            self.cmd.run()

    def test_arg_with_wrong_type(self):
        """User passed arg with wrong type. e.g string for asn"""
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--asn", "blaaaaa"])
            self.cmd.run()
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--asnv4", "blaaaaa"])
            self.cmd.run()
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--asnv6", "blaaaaa"])
            self.cmd.run()
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--limit", "blaaaaa"])
            self.cmd.run()
        with self.assertRaises(SystemExit):
            self.cmd.init_args(["--radius", "blaaaaa"])
            self.cmd.run()

    def test_location_google_breaks(self):
        """User passed location arg but google api gave error"""
        caught_exceptions = [
            requests.ConnectionError, requests.HTTPError, requests.Timeout]
        with mock.patch('requests.get') as mock_get:
            for exception in caught_exceptions:
                mock_get.side_effect = exception
                with self.assertRaises(RipeAtlasToolsException):
                    self.cmd.init_args(["--location", "blaaaa"])
                    self.cmd.run()
            mock_get.side_effect = Exception()
            with self.assertRaises(Exception):
                self.cmd.init_args(["--location", "blaaaa"])
                self.cmd.run()

    def test_location_google_wrong_output(self):
        """User passed location arg but google api gave not expected format"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"blaaa": "bla"}
                with self.assertRaises(RipeAtlasToolsException):
                    self.cmd.init_args(["--location", "blaaaa"])
                    self.cmd.run()

    def test_location_arg(self):
        """User passed location arg"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"results": [
                    {"geometry": {"location": {"lat": 1, "lng": 2}}}]}
                self.cmd.init_args(["--location", "blaaaa"])
                self.assertEquals(self.cmd.build_request_args(), {
                    "latitude": '1', "longitude": '2'})

    def test_location_arg_with_radius(self):
        """User passed location arg"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"results": [
                    {"geometry": {"location": {"lat": 1, "lng": 2}}}
                ]}
                self.cmd.init_args(["--location", "blaaaa", "--radius", "4"])
                self.assertEquals(
                    self.cmd.build_request_args(),
                    {"radius": "1,2:4"}
                )

    def test_asn_args(self):
        """User passed asn arg together with asnv4 or asnv6"""
        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args(["--asn", "3333", "--asnv4", "3333"])
            self.cmd.run()

        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args(["--asn", "3333", "--asnv6", "3333"])
            self.cmd.run()

    def test_prefix_args(self):
        """User passed prefix arg together with prefixv4 or prefixv6"""
        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args([
                "--prefix", "193.0.0.0/21",
                "--prefixv4", "193.0.0.0/21"
            ])
            self.cmd.run()

        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args([
                "--prefix", "2001:67c:2e8::/48",
                "--prefixv6", "2001:67c:2e8::/48"
            ])
            self.cmd.run()

    def test_all_args(self):
        """User passed all arguments"""
        self.cmd.init_args(["--all"])
        self.assertEquals(self.cmd.build_request_args(), {})

    def test_center_arg_wrong_value(self):
        """User passed center arg with wrong value"""
        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args(["--center", "blaaaa"])
            self.cmd.run()

    def test_center_arg(self):
        """User passed center arg"""
        self.cmd.init_args(["--center", "1,2"])
        self.assertEquals(
            self.cmd.build_request_args(),
            {"latitude": "1", "longitude": "2"}
        )

    def test_center_arg_with_radius(self):
        """User passed center and radius arg"""
        self.cmd.init_args(["--center", "1,2", "--radius", "4"])
        self.assertEquals(self.cmd.build_request_args(), {"radius": "1,2:4"})

    def test_country_arg(self):
        """User passed country code arg"""
        self.cmd.init_args(["--country-code", "GR"])
        self.assertEquals(self.cmd.build_request_args(), {"country_code": "GR"})

    def test_country_arg_with_radius(self):
        """User passed country code arg together with radius"""
        self.cmd.init_args(["--country-code", "GR", "--radius", "4"])
        self.assertEquals(self.cmd.build_request_args(), {"country_code": "GR"})

    def test_sane_args1(self):
        """User passed several arguments (1)"""
        self.cmd.init_args([
            "--center", "1,2",
            "--radius", "4",
            "--asnv4", "3333",
            "--prefix", "193.0.0.0/21"
        ])
        self.assertEquals(
            self.cmd.build_request_args(),
            {'asn_v4': 3333, 'prefix': '193.0.0.0/21', 'radius': '1,2:4'}
        )

    def test_sane_args2(self):
        """User passed several arguments (2)"""

        self.cmd.init_args([
            "--location", "Amsterdam",
            "--asn", "3333",
            "--prefixv4", "193.0.0.0/21"
        ])

        path = 'ripe.atlas.tools.commands.probes.Command.location2degrees'
        with mock.patch(path) as mock_get:
            mock_get.return_value = (1, 2)
            self.assertEquals(self.cmd.build_request_args(), {
                'asn': 3333,
                'prefix_v4': '193.0.0.0/21',
                'latitude': 1,
                'longitude': 2
            })

    def test_sane_args3(self):
        """User passed several arguments (3)"""

        self.cmd.init_args([
            "--center", "1,2",
            "--asnv6", "3333",
            "--prefixv6", "2001:67c:2e8::/48"
        ])
        self.assertEquals(self.cmd.build_request_args(), {
            'asn_v6': 3333,
            'prefix_v6': '2001:67c:2e8::/48',
            'latitude': '1',
            'longitude': '2'
        })

    def test_render_ids_only(self):
        """User passed ids_only arg, testing rendiring"""
        self.cmd.init_args([
            "--ids-only", "--country-code", "GR"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            self.assertEquals(mystdout.getvalue(), "1,2,3,4,5")

        sys.stdout = old_stdout

    def test_render_ids_only_with_limit(self):
        """User passed ids_only arg together with limit, testing rendering"""
        self.cmd.init_args([
            "--ids-only",
            "--country-code", "GR",
            "--limit", "2"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            self.assertEquals(mystdout.getvalue(), "1,2")

        sys.stdout = old_stdout

    def test_render_ids_only_with_aggr(self):
        """
        User passed ids_only arg together with aggrement, testing rendiring
        """
        self.cmd.init_args([
            "--ids-only",
            "--aggregate-by", "country_code"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            self.assertEquals(mystdout.getvalue(), "1,2,3,4,5")

        sys.stdout = old_stdout

    def test_get_aggregators(self):
        """User passed --aggregate-by args"""
        self.cmd.init_args([
            "--aggregate-by", "asn_v4",
            "--aggregate-by", "country_code",
            "--aggregate-by", "prefix_v4"
        ])
        expected_output = [
            ValueKeyAggregator(key="asn_v4"),
            ValueKeyAggregator(key="country_code"),
            ValueKeyAggregator(key="prefix_v4")
        ]
        output = self.cmd.get_aggregators()
        for index, v in enumerate(output):
            self.assertTrue(isinstance(v, ValueKeyAggregator))
            self.assertEquals(
                v.aggregation_keys,
                expected_output[index].aggregation_keys
            )

    def test_render_without_aggregation(self):
        """Tests rendering of results without aggregation"""
        self.cmd.init_args(["--limit", "4"])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            expected_output = (
                "We found the following probes with the given criteria:\n"
                "ID    ASNv4  ASNv6  CC Status      \n"
                "1     3333   None   GR None        \n"
                "2     3333   None   DE None        \n"
                "3     3332   None   DE None        \n"
                "4     3333   None   NL None        \n"
                "Total probes found: 4\n"
            )
            self.assertEquals(mystdout.getvalue(), expected_output)

        sys.stdout = old_stdout

    def test_render_without_aggregation_with_limit(self):
        """Tests rendering of results without aggregation but with limit"""
        self.cmd.init_args([
            "--country-code", "GR", "--limit", "2"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            expected_output = (
                "We found the following probes with the given criteria:\n"
                "ID    ASNv4  ASNv6  CC Status      \n"
                "1     3333   None   GR None        \n"
                "2     3333   None   DE None        \n"
                "Total probes found: 4\n"
            )
            self.assertEquals(mystdout.getvalue(), expected_output)

        sys.stdout = old_stdout

    def test_render_with_aggregation(self):
        """Tests rendering of results with aggregation"""
        self.cmd.init_args([
            "--country-code", "GR", "--aggregate-by", "country_code",
            "--aggregate-by", "asn_v4", "--aggregate-by", "prefix_v4"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            expected_output = (
                "We found the following probes with the given criteria:\n"
                "COUNTRY_CODE: NL\n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    4     3333   None   NL None        \n"
                "COUNTRY_CODE: GR\n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    1     3333   None   GR None        \n"
                "    5     3333   None   GR None        \n"
                "COUNTRY_CODE: DE\n"
                " ASN_V4: 3332\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    3     3332   None   DE None        \n"
                " ASN_V4: 3333\n  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    2     3333   None   DE None        \n"
                "Total probes found: 4\n"
            )
            self.assertEquals(mystdout.getvalue(), expected_output)

        sys.stdout = old_stdout

    def test_render_with_aggregation_with_limit(self):
        """Tests rendering of results with aggregation with limit"""
        self.cmd.init_args([
            "--country-code", "GR", "--aggregate-by", "country_code",
            "--aggregate-by", "asn_v4", "--aggregate-by", "prefix_v4",
            "--limit", "1"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            expected_output = (
                "We found the following probes with the given criteria:\n"
                "COUNTRY_CODE: GR\n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    1     3333   None   GR None        \n"
                "Total probes found: 4\n"
            )
            self.assertEquals(mystdout.getvalue(), expected_output)

        sys.stdout = old_stdout

    def test_render_with_aggregation_with_max_per_aggr(self):
        """
        Tests rendering of results with aggregation with max per aggr option
        """
        self.cmd.init_args([
            "--country-code", "GR", "--aggregate-by", "country_code",
            "--aggregate-by", "asn_v4", "--aggregate-by", "prefix_v4",
            "--max-per-aggregation", "1"
        ])

        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        path = 'ripe.atlas.tools.commands.probes.ProbeRequest'
        with mock.patch(path) as mock_get:
            mock_get.return_value = FakeGen()
            self.cmd.run()
            expected_output = (
                "We found the following probes with the given criteria:\n"
                "COUNTRY_CODE: NL\n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    4     3333   None   NL None        \n"
                "COUNTRY_CODE: GR\n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    1     3333   None   GR None        \n"
                "COUNTRY_CODE: DE\n"
                " ASN_V4: 3332\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    3     3332   None   DE None        \n"
                " ASN_V4: 3333\n"
                "  PREFIX_V4: 193.0/22\n"
                "    ID    ASNv4  ASNv6  CC Status      \n"
                "    2     3333   None   DE None        \n"
                "Total probes found: 4\n"
            )
            self.assertEquals(mystdout.getvalue(), expected_output)

        sys.stdout = old_stdout

    def test_render_args(self):
        """User passed max_per_aggr and additional fields args"""
        self.cmd.init_args([
            "--max-per-aggregation",
            "3",
            "--additional-fields",
            "blaaaa, grrrrr"
        ])
        self.assertEquals(
            self.cmd._clean_render_args(),
            {"max_per_aggr": 3, "additional_fields": ["blaaaa", "grrrrr"]}
        )
