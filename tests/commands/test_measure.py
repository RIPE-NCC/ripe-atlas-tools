# -*- coding: UTF-8 -*-

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
import tempfile
import unittest
from io import StringIO

from random import randint

from unittest import mock

from ripe.atlas.tools.commands.measure.base import Command
from ripe.atlas.tools.commands.measure import (
    PingMeasureCommand,
    TracerouteMeasureCommand,
    DnsMeasureCommand,
    SslcertMeasureCommand,
    HttpMeasureCommand,
    NtpMeasureCommand,
    SpecMeasureCommand,
)
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.tools.settings import Configuration, AliasesDB

from ..base import capture_sys_output


class TestMeasureCommand(unittest.TestCase):

    CONF = "ripe.atlas.tools.commands.measure.base.conf"
    KINDS = {
        "ping": PingMeasureCommand,
        "traceroute": TracerouteMeasureCommand,
        "dns": DnsMeasureCommand,
        "sslcert": SslcertMeasureCommand,
        "http": HttpMeasureCommand,
        "ntp": NtpMeasureCommand,
    }

    def setUp(self):
        self.maxDiff = None

    def test_no_arguments(self):
        with capture_sys_output():
            with self.assertRaises(RipeAtlasToolsException) as e:
                Command().init_args([])
            self.assertTrue(str(e.exception).startswith("Usage: ripe-atlas measure <"))

    def test_bad_type_argument(self):
        with capture_sys_output():
            with self.assertRaises(RipeAtlasToolsException) as e:
                Command().init_args(["not-a-type"])
            self.assertTrue(str(e.exception).startswith("Usage: ripe-atlas measure <"))

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_dry_run(self):

        with capture_sys_output() as (stdout, stderr):
            cmd = PingMeasureCommand()
            cmd.init_args(["ping", "--target", "ripe.net", "--dry-run"])
            cmd.run()
            expected = (
                "\n"
                "Definitions:\n"
                "================================================================================\n"  # noqa: E501
                "target                    ripe.net\n"
                "packet_interval           1000\n"
                "description               Ping measurement to ripe.net\n"
                "af                        4\n"
                "packets                   3\n"
                "size                      48\n"
                "\n"
                "Sources:\n"
                "================================================================================\n"  # noqa: E501
                "requested                 50\n"
                "type                      area\n"
                "value                     WW\n"
                "tags\n"
                "  include                 system-ipv4-works\n"
                "  exclude                 \n"
                "\n"
            )
            self.assertEqual(
                set(stdout.getvalue().split("\n")), set(expected.split("\n"))
            )

        with capture_sys_output() as (stdout, stderr):
            cmd = PingMeasureCommand()
            cmd.init_args(
                [
                    "ping",
                    "--target",
                    "ripe.net",
                    "--af",
                    "6",
                    "--include-tag",
                    "alpha",
                    "--include-tag",
                    "bravo",
                    "--include-tag",
                    "charlie",
                    "--exclude-tag",
                    "delta",
                    "--exclude-tag",
                    "echo",
                    "--exclude-tag",
                    "foxtrot",
                    "--dry-run",
                ]
            )
            cmd.run()
            expected = (
                "\n"
                "Definitions:\n"
                "================================================================================\n"  # noqa: E501
                "target                    ripe.net\n"
                "packet_interval           1000\n"
                "description               Ping measurement to ripe.net\n"
                "af                        6\n"
                "packets                   3\n"
                "size                      48\n"
                "\n"
                "Sources:\n"
                "================================================================================\n"  # noqa: E501
                "requested                 50\n"
                "type                      area\n"
                "value                     WW\n"
                "tags\n"
                "  include                 alpha, bravo, charlie\n"
                "  exclude                 delta, echo, foxtrot\n"
                "\n"
            )
            self.assertEqual(
                set(stdout.getvalue().split("\n")), set(expected.split("\n"))
            )

    def test_clean_target(self):

        cmd = PingMeasureCommand()
        with capture_sys_output():
            cmd.init_args(["ping", "--target", "ripe.net"])
            self.assertEqual(cmd.clean_target(), "ripe.net")

        cmd = DnsMeasureCommand()
        with capture_sys_output():
            cmd.init_args(["dns", "--query-argument", "ripe.net"])
            self.assertEqual(cmd.clean_target(), None)

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_ping(self):

        spec = Configuration.DEFAULT["specification"]["types"]["ping"]

        cmd = PingMeasureCommand()
        cmd.init_args(["ping", "--target", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Ping measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "packet_interval": spec["packet-interval"],
                "size": spec["size"],
            },
        )

        # Test using positional target
        cmd = PingMeasureCommand()
        cmd.init_args(["ping", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Ping measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "packet_interval": spec["packet-interval"],
                "size": spec["size"],
            },
        )

        cmd = PingMeasureCommand()
        cmd.init_args(
            [
                "ping",
                "--target",
                "ripe.net",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--packets",
                "7",
                "--packet-interval",
                "200",
                "--size",
                "24",
                "--group-id",
                "1000001",
                "--include-probe-id",
                "--spread",
                "60",
                "--resolve-on-probe",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "packets": 7,
                "packet_interval": 200,
                "size": 24,
                "group_id": 1000001,
                "include_probe_id": True,
                "spread": 60,
                "resolve_on_probe": True,
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_traceroute(self):

        spec = Configuration.DEFAULT["specification"]["types"]["traceroute"]

        cmd = TracerouteMeasureCommand()
        cmd.init_args(["traceroute", "--target", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Traceroute measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "size": spec["size"],
                "destination_option_size": spec["destination-option-size"],
                "hop_by_hop_option_size": spec["hop-by-hop-option-size"],
                "dont_fragment": spec["dont-fragment"],
                "first_hop": spec["first-hop"],
                "max_hops": spec["max-hops"],
                "paris": spec["paris"],
                "port": spec["port"],
                "protocol": spec["protocol"],
                "timeout": spec["timeout"],
            },
        )

        # Test using positional target
        cmd = TracerouteMeasureCommand()
        cmd.init_args(["traceroute", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Traceroute measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "size": spec["size"],
                "destination_option_size": spec["destination-option-size"],
                "hop_by_hop_option_size": spec["hop-by-hop-option-size"],
                "dont_fragment": spec["dont-fragment"],
                "first_hop": spec["first-hop"],
                "max_hops": spec["max-hops"],
                "paris": spec["paris"],
                "port": spec["port"],
                "protocol": spec["protocol"],
                "timeout": spec["timeout"],
            },
        )

        cmd = TracerouteMeasureCommand()
        cmd.init_args(
            [
                "traceroute",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--target",
                "ripe.net",
                "--packets",
                "7",
                "--size",
                "24",
                "--destination-option-size",
                "12",
                "--hop-by-hop-option-size",
                "13",
                "--dont-fragment",
                "--first-hop",
                "2",
                "--max-hops",
                "5",
                "--paris",
                "8",
                "--port",
                "123",
                "--protocol",
                "TCP",
                "--timeout",
                "1500",
                "--duplicate-timeout",
                "500",
                "--response-timeout",
                "500",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "packets": 7,
                "size": 24,
                "destination_option_size": 12,
                "hop_by_hop_option_size": 13,
                "dont_fragment": True,
                "first_hop": 2,
                "max_hops": 5,
                "paris": 8,
                "port": 123,
                "protocol": "TCP",
                "timeout": 1500,
                "duplicate_timeout": 500,
                "response_timeout": 500,
            },
        )

        """Tests for the protocol provided in lower case"""
        cmd = TracerouteMeasureCommand()
        cmd.init_args(["traceroute", "--target", "ripe.net", "--protocol", "icmp"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Traceroute measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "size": spec["size"],
                "destination_option_size": spec["destination-option-size"],
                "hop_by_hop_option_size": spec["hop-by-hop-option-size"],
                "dont_fragment": spec["dont-fragment"],
                "first_hop": spec["first-hop"],
                "max_hops": spec["max-hops"],
                "paris": spec["paris"],
                "port": spec["port"],
                "protocol": "ICMP",
                "timeout": spec["timeout"],
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_dns(self):

        spec = Configuration.DEFAULT["specification"]["types"]["dns"]

        cmd = DnsMeasureCommand()
        cmd.init_args(["dns", "--query-argument", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": spec["query-class"],
                "query_type": spec["query-type"],
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "tls": False,
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

        # Test using positional query argument
        cmd = DnsMeasureCommand()
        cmd.init_args(["dns", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": spec["query-class"],
                "query_type": spec["query-type"],
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "tls": False,
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

        cmd = DnsMeasureCommand()
        cmd.init_args(
            [
                "dns",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--target",
                "non-existent-dns.ripe.net",
                "--query-class",
                "CHAOS",
                "--query-type",
                "SOA",
                "--query-argument",
                "some arbitrary string",
                "--set-cd-bit",
                "--set-do-bit",
                "--set-rd-bit",
                "--set-nsid-bit",
                "--protocol",
                "TCP",
                "--retry",
                "2",
                "--udp-payload-size",
                "512",
                "--timeout",
                "500",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "non-existent-dns.ripe.net",
                "query_class": "CHAOS",
                "query_type": "SOA",
                "query_argument": "some arbitrary string",
                "set_cd_bit": True,
                "set_do_bit": True,
                "set_rd_bit": True,
                "set_nsid_bit": True,
                "protocol": "TCP",
                "retry": 2,
                "udp_payload_size": 512,
                "use_probe_resolver": False,
                "timeout": 500,
                "tls": False,
            },
        )

        """Testing for protocol argument in lower case"""
        cmd = DnsMeasureCommand()
        cmd.init_args(["dns", "--query-argument", "ripe.net", "--protocol", "tcp"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": spec["query-class"],
                "query_type": spec["query-type"],
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "tls": False,
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": "TCP",
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

        """Testing for query class in lower case"""
        cmd = DnsMeasureCommand()
        cmd.init_args(["dns", "--query-argument", "ripe.net", "--query-class", "in"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": "IN",
                "query_type": spec["query-type"],
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "tls": False,
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

        """Testing for query type in lower case"""
        cmd = DnsMeasureCommand()
        cmd.init_args(
            [
                "dns",
                "--query-argument",
                "ripe.net",
                "--query-type",
                "txt",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": spec["query-class"],
                "query_type": "TXT",
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "tls": False,
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

        """Explicitly unset bits"""
        cmd = DnsMeasureCommand()
        cmd.init_args(
            [
                "dns",
                "--query-argument",
                "ripe.net",
                "--query-type",
                "txt",
                "--no-set-cd-bit",
                "--no-set-do-bit",
                "--no-set-rd-bit",
                "--no-set-nsid-bit",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "DNS measurement for ripe.net",
                "query_class": spec["query-class"],
                "query_type": "TXT",
                "query_argument": "ripe.net",
                "set_cd_bit": False,
                "set_do_bit": False,
                "set_rd_bit": False,
                "tls": False,
                "set_nsid_bit": False,
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_sslcert(self):

        spec = Configuration.DEFAULT["specification"]["types"]["sslcert"]

        cmd = SslcertMeasureCommand()
        cmd.init_args(["sslcert", "--target", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Sslcert measurement to ripe.net",
                "target": "ripe.net",
                "port": spec["port"],
            },
        )

        # Test using positional target
        cmd = SslcertMeasureCommand()
        cmd.init_args(["sslcert", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Sslcert measurement to ripe.net",
                "target": "ripe.net",
                "port": spec["port"],
            },
        )

        cmd = SslcertMeasureCommand()
        cmd.init_args(
            [
                "sslcert",
                "--target",
                "ripe.net",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--port",
                "7",
                "--hostname",
                "ripe.net",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "port": 7,
                "hostname": "ripe.net",
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_http(self):

        spec = Configuration.DEFAULT["specification"]["types"]["http"]

        cmd = HttpMeasureCommand()
        cmd.init_args(["http", "--target", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Http measurement to ripe.net",
                "target": "ripe.net",
                "header_bytes": spec["header-bytes"],
                "version": spec["version"],
                "method": spec["method"],
                "port": spec["port"],
                "path": spec["path"],
                "query_string": spec["query-string"],
                "user_agent": spec["user-agent"],
                "max_bytes_read": spec["body-bytes"],
            },
        )

        # Test using positional target
        cmd = HttpMeasureCommand()
        cmd.init_args(["http", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Http measurement to ripe.net",
                "target": "ripe.net",
                "header_bytes": spec["header-bytes"],
                "version": spec["version"],
                "method": spec["method"],
                "port": spec["port"],
                "path": spec["path"],
                "query_string": spec["query-string"],
                "user_agent": spec["user-agent"],
                "max_bytes_read": spec["body-bytes"],
            },
        )

        cmd = HttpMeasureCommand()
        cmd.init_args(
            [
                "http",
                "--target",
                "ripe.net",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--header-bytes",
                "100",
                "--version",
                "99",
                "--method",
                "a-method",
                "--port",
                "7",
                "--path",
                "/path/to/something",
                "--query-string",
                "x=7",
                "--user-agent",
                "This is my custom user agent",
                "--body-bytes",
                "200",
                "--timing-verbosity",
                "2",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "header_bytes": 100,
                "version": "99",
                "method": "a-method",
                "port": 7,
                "path": "/path/to/something",
                "query_string": "x=7",
                "user_agent": "This is my custom user agent",
                "max_bytes_read": 200,
                "extended_timing": True,
                "more_extended_timing": True,
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_measurement_kwargs_ntp(self):

        spec = Configuration.DEFAULT["specification"]["types"]["ntp"]

        cmd = NtpMeasureCommand()
        cmd.init_args(["ntp", "--target", "ripe.net"])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": "Ntp measurement to ripe.net",
                "target": "ripe.net",
                "packets": spec["packets"],
                "timeout": spec["timeout"],
            },
        )

        cmd = NtpMeasureCommand()
        cmd.init_args(
            [
                "ntp",
                "--target",
                "ripe.net",
                "--af",
                "6",
                "--description",
                "This is my description",
                "--packets",
                "6",
                "--timeout",
                "9000",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "packets": 6,
                "timeout": 9000,
            },
        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_get_source_kwargs(self):

        spec = Configuration.DEFAULT["specification"]

        for kind, klass in self.KINDS.items():

            cmd = klass()
            args = [kind, "--target", "example.com"]
            if kind == "dns":
                args = ["dns", "--query-argument", "example.com"]

            cmd.init_args(list(args))

            tags = spec["tags"]["ipv{}".format(cmd._get_af())]
            includes = tags[kind]["include"] + tags["all"]["include"]
            excludes = tags[kind]["exclude"] + tags["all"]["exclude"]

            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": spec["source"]["requested"],
                    "type": spec["source"]["type"],
                    "value": spec["source"]["value"],
                    "tags": {"include": includes, "exclude": excludes},
                },
            )

            cmd = klass()
            cmd.init_args(args + ["--probes", "10", "--from-country", "ca"])
            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": 10,
                    "type": "country",
                    "value": "CA",
                    "tags": {"include": includes, "exclude": excludes},
                },
            )

            for area in (
                "WW",
                "West",
                "North-Central",
                "South-Central",
                "North-East",
                "South-East",
            ):
                cmd = klass()
                cmd.init_args(args + ["--probes", "10", "--from-area", area])
                self.assertEqual(
                    cmd._get_source_kwargs(),
                    {
                        "requested": 10,
                        "type": "area",
                        "value": area,
                        "tags": {"include": includes, "exclude": excludes},
                    },
                )

            cmd = klass()
            cmd.init_args(args + ["--probes", "10", "--from-prefix", "1.2.3.0/22"])
            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": 10,
                    "type": "prefix",
                    "value": "1.2.3.0/22",
                    "tags": {"include": includes, "exclude": excludes},
                },
            )

            cmd = klass()
            cmd.init_args(args + ["--probes", "10", "--from-asn", "3333"])
            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": 10,
                    "type": "asn",
                    "value": 3333,
                    "tags": {"include": includes, "exclude": excludes},
                },
            )

            # Try 20 permutations of probe lists
            for __ in range(0, 20):
                requested = randint(1, 500)
                selection = [str(randint(1, 5000)) for _ in range(0, 100)]
                cmd = klass()
                cmd.init_args(
                    args
                    + ["--probes", str(requested), "--from-probes", ",".join(selection)]
                )
                self.assertEqual(
                    cmd._get_source_kwargs(),
                    {
                        "requested": requested,
                        "type": "probes",
                        "value": ",".join(selection),
                        "tags": {"include": includes, "exclude": excludes},
                    },
                )

            cmd = klass()
            cmd.init_args(args + ["--probes", "10", "--from-measurement", "1001"])
            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": 10,
                    "type": "msm",
                    "value": 1001,
                    "tags": {"include": includes, "exclude": excludes},
                },
            )

            cmd = klass()
            cmd.init_args(
                args
                + ["--include-tag", "tag-to-include", "--exclude-tag", "tag-to-exclude"]
            )
            self.assertEqual(
                cmd._get_source_kwargs(),
                {
                    "requested": spec["source"]["requested"],
                    "type": spec["source"]["type"],
                    "value": spec["source"]["value"],
                    "tags": {
                        "include": ["tag-to-include"],
                        "exclude": ["tag-to-exclude"],
                    },
                },
            )

    def test_get_af(self):

        conf = copy.deepcopy(Configuration.DEFAULT)
        conf["specification"]["af"] = 100

        for kind, klass in self.KINDS.items():
            with mock.patch(self.CONF, conf):

                for af in (4, 6):
                    cmd = klass()
                    cmd.init_args([kind, "--af", str(af)])
                    self.assertEqual(cmd._get_af(), af)

                cmd = klass()
                cmd.init_args([kind, "--target", "1.2.3.4"])
                self.assertEqual(cmd._get_af(), 4)

                cmd = klass()
                cmd.init_args([kind, "--target", "1:2:3:4:5:6:7:8"])
                self.assertEqual(cmd._get_af(), 6)

                cmd = klass()
                cmd.init_args([kind, "--target", "1.2.3.4.5"])
                self.assertEqual(cmd._get_af(), conf["specification"]["af"])

    def test_handle_api_error(self):

        cmd = Command()

        plain_error = "This is a plain text error"

        with self.assertRaises(RipeAtlasToolsException) as e:
            cmd._handle_api_error(plain_error)
        self.assertIn(plain_error, str(e.exception))

        err_obj = {"detail": "This is a formatted error"}

        with self.assertRaises(RipeAtlasToolsException) as e:
            cmd._handle_api_error(err_obj)
        self.assertIn(json.dumps(err_obj, indent=2), str(e.exception))

    def test_add_arguments(self):

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--set-alias", "\\invalid"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --set-alias: "
                '"\\invalid" does not appear to be a valid alias.',
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--renderer", "not-a-renderer"])
            self.assertTrue(
                stderr.getvalue()
                .split("\n")[-2]
                .startswith(
                    "ripe-atlas measure: error: argument --renderer: invalid "
                    "choice: 'not-a-renderer' (choose from"
                )
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--af", "5"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --af: invalid choice: 5 "
                "(choose from 4, 6)",
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--target", "not a target"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --target: "
                '"not a target" does not appear to be an IP address or host '
                "name",
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--from-area", "not an area"])
            self.assertTrue(
                stderr.getvalue()
                .split("\n")[-2]
                .startswith(
                    "ripe-atlas measure: error: argument --from-area: invalid "
                    "choice:"
                )
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                PingMeasureCommand().init_args(["ping", "--from-probes", "0,50000"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --from-probes: 0 "
                "is lower than the minimum permitted value of 1.",
            )

        for clude in ("in", "ex"):
            with capture_sys_output() as (stdout, stderr):
                for tag in ("NotATag", "tag!", "not a tag", "νοτ α ταγ"):
                    with self.assertRaises(SystemExit):
                        PingMeasureCommand().init_args(
                            ["ping", "--{}clude-tag".format(clude), tag]
                        )
                    self.assertEqual(
                        stderr.getvalue().split("\n")[-2],
                        "ripe-atlas measure: error: argument --{}clude-tag: "
                        '"{}" does not appear to be a valid tag.'.format(clude, tag),
                    )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                TracerouteMeasureCommand().init_args(
                    ["traceroute", "--protocol", "invalid"]
                )
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --protocol: invalid "
                "choice: 'INVALID' (choose from 'ICMP', 'UDP', 'TCP')",
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                DnsMeasureCommand().init_args(["dns", "--protocol", "invalid"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --protocol: invalid "
                "choice: 'INVALID' (choose from 'UDP', 'TCP')",
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                HttpMeasureCommand().init_args(["http", "--timing-verbosity", "3"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --timing-verbosity: "
                "invalid choice: 3 (choose from 0, 1, 2)",
            )

        min_options = [
            ("from-measurement", ((PingMeasureCommand,), 1)),
            ("probes", ((PingMeasureCommand,), 1)),
            ("timeout", ((TracerouteMeasureCommand,), 1)),
        ]
        for option, (klasses, minimum) in min_options:
            for klass in klasses:
                with capture_sys_output() as (stdout, stderr):
                    test_value = minimum - 1
                    with self.assertRaises(SystemExit):
                        klass().init_args(
                            [
                                klass.__name__.replace("MeasureCommand", "").lower(),
                                "--{}".format(option),
                                str(test_value),
                            ]
                        )
                    self.assertEqual(
                        stderr.getvalue().split("\n")[-2],
                        "ripe-atlas measure: error: argument --{}: "
                        "The integer must be greater than {}.".format(option, minimum),
                    )

        min_max_options = [
            ("from-asn", ((PingMeasureCommand,), (1, 2 ** 32 - 2))),
            ("paris", ((TracerouteMeasureCommand,), (0, 64))),
            ("first-hop", ((TracerouteMeasureCommand,), (1, 255))),
            ("max-hops", ((TracerouteMeasureCommand,), (1, 255))),
            (
                "port",
                (
                    (
                        TracerouteMeasureCommand,
                        SslcertMeasureCommand,
                        HttpMeasureCommand,
                    ),
                    (1, 65535),
                ),
            ),
            ("header-bytes", ((HttpMeasureCommand,), (0, 2048))),
            ("body-bytes", ((HttpMeasureCommand,), (1, 1020048))),
            ("size", ((PingMeasureCommand,), (1, 2048))),
            ("size", ((TracerouteMeasureCommand,), (0, 2048))),
            (
                "packets",
                (
                    (
                        PingMeasureCommand,
                        TracerouteMeasureCommand,
                        NtpMeasureCommand,
                    ),
                    (1, 16),
                ),
            ),
            ("packet-interval", ((PingMeasureCommand,), (2, 30000))),
            ("timeout", ((NtpMeasureCommand,), (1, 60000))),
            ("destination-option-size", ((TracerouteMeasureCommand,), (0, 1024))),
            ("hop-by-hop-option-size", ((TracerouteMeasureCommand,), (0, 2048))),
            ("retry", ((DnsMeasureCommand,), (0, 10))),
            ("udp-payload-size", ((DnsMeasureCommand,), (512, 4096))),
        ]
        for option, (klasses, extremes) in min_max_options:
            for klass in klasses:
                lower = extremes[0] - 1
                upper = extremes[1] + 1
                for invalid in lower, upper:
                    with capture_sys_output() as (stdout, stderr):
                        try:
                            klass().init_args(
                                [
                                    klass.__name__.replace(
                                        "MeasureCommand", ""
                                    ).lower(),
                                    "--{}".format(option),
                                    str(invalid),
                                ]
                            )
                        except SystemExit:
                            pass
                        else:
                            self.fail(
                                "--{} for {} should fail for value {}".format(
                                    option, klass.__name__, invalid
                                )
                            )
                        self.assertEqual(
                            stderr.getvalue().split("\n")[-2],
                            "ripe-atlas measure: error: argument --{}: The "
                            "integer must be between {} and {}.".format(
                                option, extremes[0], extremes[1]
                            ),
                        )

    @mock.patch(CONF, Configuration.DEFAULT)
    def test_account_for_selected_probes(self):

        spec = Configuration.DEFAULT["specification"]

        cmd = PingMeasureCommand()
        cmd.init_args(["ping", "--target", "ripe.net"])
        cmd._account_for_selected_probes(),
        self.assertEqual(cmd.arguments.probes, spec["source"]["requested"])

        cmd = PingMeasureCommand()
        cmd.init_args(["ping", "--target", "ripe.net", "--probes", "7"])
        cmd._account_for_selected_probes(),
        self.assertEqual(cmd.arguments.probes, 7)

        cmd = PingMeasureCommand()
        cmd.init_args(["ping", "--target", "ripe.net", "--from-probes", "1,2"])
        cmd._account_for_selected_probes(),
        self.assertEqual(cmd.arguments.probes, 2)

        cmd = PingMeasureCommand()
        cmd.init_args(
            ["ping", "--target", "ripe.net", "--from-probes", "1,2", "--probes", "7"]
        )
        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(RipeAtlasToolsException):
                cmd._account_for_selected_probes(),

    def test_set_alias(self):
        path_aliases = "ripe.atlas.tools.commands.measure.base.aliases"
        new_aliases = copy.deepcopy(AliasesDB.DEFAULT)

        with mock.patch(path_aliases, new_aliases):
            path_AliasesDB = "ripe.atlas.tools.commands.measure.base.AliasesDB"
            with mock.patch(path_AliasesDB, autospec=True) as new_AliasesDB:
                new_AliasesDB.write.return_value = True

                path_create = "ripe.atlas.tools.commands.measure.base.Command.create"
                with mock.patch(path_create) as mock_create:
                    mock_create.return_value = (True, {"measurements": [1234]})
                    cmd = PingMeasureCommand()
                    cmd.init_args(
                        [
                            "ping",
                            "--target",
                            "www.ripe.net",
                            "--no-report",
                            "--set-alias",
                            "PING_RIPE",
                        ]
                    )
                    cmd.run()
                    self.assertEqual(new_aliases["measurement"]["PING_RIPE"], 1234)

    def test_spec_valid(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", '{"type": "ping", "target": "1.2.3.4"}'])
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 4,
                "description": "Ping measurement",
                "target": "1.2.3.4",
                "type": "ping",
            },
        )

    def test_spec_valid_target(self):
        # Override target on command-line
        cmd = SpecMeasureCommand()
        cmd.init_args(
            ["spec", '{"type": "ping", "target": "1.2.3.4"}', "--target", "5.6.7.8"]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 4,
                "description": "Ping measurement",
                "target": "5.6.7.8",
                "type": "ping",
            },
        )

    def test_spec_valid_description(self):
        # Specify a custom description
        cmd = SpecMeasureCommand()
        cmd.init_args(
            [
                "spec",
                '{"type": "ping", "target": "1.2.3.4"}',
                "--description",
                "A real cool measurement",
            ]
        )
        self.assertEqual(
            cmd._get_measurement_kwargs(),
            {
                "af": 4,
                "description": "A real cool measurement",
                "target": "1.2.3.4",
                "type": "ping",
            },
        )

    def test_spec_valid_file(self):
        # Specify a valid JSON file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            filename = f.name
            f.write('{"target": "1.2.3.4", "type": "ping"}\n')
        try:
            cmd = SpecMeasureCommand()
            cmd.init_args(["spec", f"@{filename}"])
            self.assertEqual(
                cmd._get_measurement_kwargs(),
                {
                    "af": 4,
                    "description": "Ping measurement",
                    "target": "1.2.3.4",
                    "type": "ping",
                },
            )
        finally:
            os.unlink(filename)

    def test_spec_valid_stdin(self):
        # Pass valid JSON to stdin
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", "@-"])
        with mock.patch(
            "sys.stdin", StringIO('{"type": "ping", "target": "1.2.3.4"}\n')
        ):
            self.assertEqual(
                cmd._get_measurement_kwargs(),
                {
                    "af": 4,
                    "description": "Ping measurement",
                    "target": "1.2.3.4",
                    "type": "ping",
                },
            )

    def test_spec_invalid_no_type(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", '{"target": "1.2.3.4"}'])
        self.assertRaises(
            RipeAtlasToolsException,
            cmd._get_measurement_kwargs,
        )

    def test_spec_invalid_unknown_type(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", '{"type": "funnytype", "target": "1.2.3.4"}'])
        self.assertRaises(
            RipeAtlasToolsException,
            cmd._get_measurement_kwargs,
        )

    def test_spec_invalid_no_file(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", "@/this/path/does/not/exist}"])
        self.assertRaises(
            RipeAtlasToolsException,
            cmd._get_measurement_kwargs,
        )

    def test_spec_invalid_json(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", "{lkdsjf]]"])
        self.assertRaises(
            RipeAtlasToolsException,
            cmd._get_measurement_kwargs,
        )

    def test_spec_invalid_not_dict(self):
        cmd = SpecMeasureCommand()
        cmd.init_args(["spec", "[]"])
        self.assertRaises(
            RipeAtlasToolsException,
            cmd._get_measurement_kwargs,
        )
