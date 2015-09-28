import mock
import unittest
import requests
from ripe.atlas.tools.commands.findprobe import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException


class TestFindProbe(unittest.TestCase):
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
        caught_exceptions = [requests.ConnectionError, requests.HTTPError, requests.Timeout]
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
                mock_json.return_value = {"results": [{"geometry": {"location": {"lat": 1, "lng": 2}}}]}
                self.cmd.init_args(["--location", "blaaaa"])
                self.assertEquals(self.cmd.build_request_args(), {"latitude": 1, "longitude": 2})

    def test_location_arg_with_radius(self):
        """User passed location arg"""
        with mock.patch('requests.get') as mock_get:
            mock_get.return_value = requests.Response()
            with mock.patch('requests.Response.json') as mock_json:
                mock_json.return_value = {"results": [{"geometry": {"location": {"lat": 1, "lng": 2}}}]}
                self.cmd.init_args(["--location", "blaaaa", "--radius", "4"])
                self.assertEquals(self.cmd.build_request_args(), {"center": "1,2", "distance": 4})

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
            self.cmd.init_args(["--prefix", "193.0.0.0/21", "--prefixv4", "193.0.0.0/21"])
            self.cmd.run()

        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args(["--prefix", "2001:67c:2e8::/48", "--prefixv6", "2001:67c:2e8::/48"])
            self.cmd.run()

    def test_all_args(self):
        """User passed all arguments"""
        self.cmd.init_args(["--all"])
        self.assertEquals(self.cmd.build_request_args(), {})

    def test_point_arg_wrong_value(self):
        """User passed point arg with wrong value"""
        with self.assertRaises(RipeAtlasToolsException):
            self.cmd.init_args(["--point", "blaaaa"])
            self.cmd.run()

    def test_point_arg(self):
        """User passed point arg"""
        self.cmd.init_args(["--point", "1,2"])
        self.assertEquals(self.cmd.build_request_args(), {"latitude": "1", "longitude": "2"})

    def test_point_arg_with_radius(self):
        """User passed point and radius arg"""
        self.cmd.init_args(["--point", "1,2", "--radius", "4"])
        self.assertEquals(self.cmd.build_request_args(), {"center": "1,2", "distance": 4})

    def test_country_arg(self):
        """User passed country code arg"""
        self.cmd.init_args(["--country-code", "GR"])
        self.assertEquals(self.cmd.build_request_args(), {"country_code": "GR"})

    def test_country_arg_with_radius(self):
        """User passed country code arg together with radius"""
        self.cmd.init_args(["--country-code", "GR", "--radius", "4"])
        self.assertEquals(self.cmd.build_request_args(), {"country_code": "GR"})

    def test_sane_args1(self):
        """User passed several arguments."""
        self.cmd.init_args(["--point", "1,2", "--radius", "4", "--asnv4", "3333", "--prefix", "193.0.0.0/21"])
        self.assertEquals(self.cmd.build_request_args(), {'asn_v4': 3333, 'prefix': '193.0.0.0/21', 'center': '1,2', 'distance': 4})

    def test_sane_args2(self):
        """User passed several arguments."""
        self.cmd.init_args(["--location", "Amsterdam", "--asn", "3333", "--prefixv4", "193.0.0.0/21"])
        with mock.patch('ripe.atlas.tools.commands.findprobe.Command.location2degrees') as mock_get:
            mock_get.return_value = (1, 2)
            self.assertEquals(self.cmd.build_request_args(), {'asn': 3333, 'prefix_v4': '193.0.0.0/21', 'latitude': '1', 'longitude': '2'})

    def test_sane_args3(self):
        """User passed several arguments."""
        self.cmd.init_args(["--point", "1,2", "--asnv6", "3333", "--prefixv6", "2001:67c:2e8::/48"])
        self.assertEquals(self.cmd.build_request_args(), {'asn_v6': 3333, 'prefix_v6': '2001:67c:2e8::/48', 'latitude': '1', 'longitude': '2'})
