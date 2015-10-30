# -*- coding: UTF-8 -*-

import copy
import unittest

from random import randint

# Python 3 comes with mock in unittest
try:
    from unittest import mock
except ImportError:
    import mock

from ripe.atlas.tools.commands.measure import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.tools.settings import Configuration

from ..base import capture_sys_output


class TestMeasureCommand(unittest.TestCase):

    CONF = "ripe.atlas.tools.commands.measure.conf"
    KINDS = ("ping", "traceroute", "dns", "ssl", "ntp",)

    def setUp(self):
        self.cmd = Command()
        self.maxDiff = None

    def test_no_arguments(self):
        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args([])
                self.cmd.run()
            self.assertEqual(
                "ripe-atlas measure: error: too few arguments",
                stderr.getvalue().split("\n")[-2]
            )

    def test_types_no_arguments(self):

        for kind in ("ping", "traceroute", "ssl", "ntp",):
            with capture_sys_output():
                with self.assertRaises(RipeAtlasToolsException) as e:
                    self.cmd.init_args([kind])
                    self.cmd.run()
                self.assertEqual(
                    str(e.exception),
                    "You must specify a target for that kind of measurement"
                )

        with capture_sys_output():
            with self.assertRaises(RipeAtlasToolsException) as e:
                self.cmd.init_args(["dns"])
                self.cmd.run()
            self.assertEqual(
                str(e.exception),
                "At a minimum, DNS measurements require a query argument."
            )

    def test_bad_type_argument(self):
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["not-a-type"])

    def test_dry_run(self):
        with capture_sys_output() as (stdout, stderr):
            self.cmd.init_args(["ping", "--target", "ripe.net", "--dry-run"])
            self.cmd.run()
            expected = (
                "\n"
                "Definitions:\n"
                "================================================================================\n"
                "target                    ripe.net\n"
                "packet_interval           1000\n"
                "description               \n"
                "af                        4\n"
                "packets                   3\n"
                "size                      48\n"
                "\n"
                "Sources:\n"
                "================================================================================\n"
                "requested                 50\n"
                "type                      area\n"
                "value                     WW\n"
                "tags\n"
                "  include                 system-ipv4-works\n"
                "  exclude                 \n"
                "\n"
            )
            self.assertEqual(stdout.getvalue(), expected)

        with capture_sys_output() as (stdout, stderr):
            self.cmd.init_args([
                "ping",
                "--target", "ripe.net",
                "--af", "6",
                "--include-tag", "alpha",
                "--include-tag", "bravo",
                "--include-tag", "charlie",
                "--exclude-tag", "delta",
                "--exclude-tag", "echo",
                "--exclude-tag", "foxtrot",
                "--dry-run"
            ])
            self.cmd.run()
            expected = (
                "\n"
                "Definitions:\n"
                "================================================================================\n"
                "target                    ripe.net\n"
                "packet_interval           1000\n"
                "description               \n"
                "af                        6\n"
                "packets                   3\n"
                "size                      48\n"
                "\n"
                "Sources:\n"
                "================================================================================\n"
                "requested                 50\n"
                "type                      area\n"
                "value                     WW\n"
                "tags\n"
                "  include                 alpha, bravo, charlie\n"
                "  exclude                 delta, echo, foxtrot\n"
                "\n"
            )
            self.assertEqual(stdout.getvalue(), expected)

    def test_clean_target(self):

        with capture_sys_output():
            self.cmd.init_args(["ping", "--target", "ripe.net"])
            self.assertEqual(self.cmd.clean_target(), "ripe.net")

        with capture_sys_output():
            self.cmd.init_args(["dns"])
            self.assertEqual(self.cmd.clean_target(), None)

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_clean_protocol(self):

        spec = Configuration.DEFAULT["specification"]["types"]

        self.cmd.init_args(["traceroute", "--protocol", "UDP"])
        self.assertEqual(self.cmd.clean_protocol(), "UDP")
        self.assertEqual(self.cmd.arguments.protocol, "UDP")

        self.cmd.init_args(["traceroute", "--protocol", "TCP"])
        self.assertEqual(self.cmd.clean_protocol(), "TCP")
        self.assertEqual(self.cmd.arguments.protocol, "TCP")

        self.cmd.init_args(["traceroute", "--protocol", "ICMP"])
        self.assertEqual(self.cmd.clean_protocol(), "ICMP")
        self.assertEqual(self.cmd.arguments.protocol, "ICMP")

        self.cmd.init_args(["traceroute"])
        self.assertEqual(
            self.cmd.clean_protocol(), spec["traceroute"]["protocol"])
        self.assertEqual(
            self.cmd.arguments.protocol, spec["traceroute"]["protocol"])

        self.cmd.init_args(["dns", "--protocol", "UDP"])
        self.assertEqual(self.cmd.clean_protocol(), "UDP")
        self.assertEqual(self.cmd.arguments.protocol, "UDP")

        self.cmd.init_args(["dns", "--protocol", "TCP"])
        self.assertEqual(self.cmd.clean_protocol(), "TCP")
        self.assertEqual(self.cmd.arguments.protocol, "TCP")

        self.cmd.init_args(["dns"])
        self.assertEqual(self.cmd.clean_protocol(), spec["dns"]["protocol"])
        self.assertEqual(self.cmd.arguments.protocol, spec["dns"]["protocol"])

        for kind in ("ping", "ssl", "ntp"):
            with self.assertRaises(RipeAtlasToolsException) as e:
                self.cmd.init_args([kind])
                self.cmd.clean_protocol()
            self.assertEqual(
                str(e.exception),
                "Measurements of type \"{}\" have no use for a "
                "protocol value.".format(kind)
            )

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_clean_shared_option(self):

        spec = Configuration.DEFAULT["specification"]["types"]
        for kind in ("ping", "traceroute"):

            self.cmd.init_args([kind, "--size", "25", "--packets", "6"])
            self.assertEqual(self.cmd.clean_shared_option("ping", "size"), 25)
            self.assertEqual(self.cmd.clean_shared_option("ping", "packets"), 6)

            self.cmd.init_args([kind])
            self.assertEqual(
                self.cmd.clean_shared_option(kind, "size"), spec[kind]["size"])

            self.cmd.init_args(["ping"])
            self.assertEqual(
                self.cmd.clean_shared_option(kind, "packets"),
                spec[kind]["packets"]
            )

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_get_measurement_kwargs_ping(self):

        spec = Configuration.DEFAULT["specification"]["types"]["ping"]

        self.cmd.init_args([
            "ping", "--target", "ripe.net"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": Configuration.DEFAULT["specification"]["description"],
                "target": "ripe.net",
                "packets": spec["packets"],
                "packet_interval": spec["packet-interval"],
                "size": spec["size"]
            }
        )

        self.cmd.init_args([
            "ping",
            "--target", "ripe.net",
            "--af", "6",
            "--description", "This is my description",
            "--packets", "7",
            "--packet-interval", "200",
            "--size", "24"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
            {
                "af": 6,
                "description": "This is my description",
                "target": "ripe.net",
                "packets": 7,
                "packet_interval": 200,
                "size": 24
            }
        )

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_get_measurement_kwargs_traceroute(self):

        spec = Configuration.DEFAULT["specification"]["types"]["traceroute"]

        self.cmd.init_args([
            "traceroute", "--target", "ripe.net"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": Configuration.DEFAULT["specification"]["description"],
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
                "timeout": spec["timeout"]
            }
        )

        self.cmd.init_args([
            "traceroute",
            "--af", "6",
            "--description", "This is my description",
            "--target", "ripe.net",
            "--packets", "7",
            "--size", "24",
            "--destination-option-size", "12",
            "--hop-by-hop-option-size", "13",
            "--dont-fragment",
            "--first-hop", "2",
            "--max-hops", "5",
            "--paris", "8",
            "--port", "123",
            "--protocol", "TCP",
            "--timeout", "1500"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
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
                "timeout": 1500
            }
        )

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_get_measurement_kwargs_dns(self):

        spec = Configuration.DEFAULT["specification"]["types"]["dns"]

        self.cmd.init_args([
            "dns", "--query-argument", "ripe.net"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
            {
                "af": Configuration.DEFAULT["specification"]["af"],
                "description": Configuration.DEFAULT["specification"]["description"],
                "query_class": spec["query-class"],
                "query_type": spec["query-type"],
                "query_argument": "ripe.net",
                "set_cd_bit": spec["set-cd-bit"],
                "set_do_bit": spec["set-do-bit"],
                "set_rd_bit": spec["set-rd-bit"],
                "set_nsid_bit": spec["set-nsid-bit"],
                "protocol": spec["protocol"],
                "retry": spec["retry"],
                "udp_payload_size": spec["udp-payload-size"],
                "use_probe_resolver": True,
            }
        )

        self.cmd.init_args([
            "dns",
            "--af", "6",
            "--description", "This is my description",
            "--target", "non-existent-dns.ripe.net",
            "--query-class", "CHAOS",
            "--query-type", "SOA",
            "--query-argument", "some arbitrary string",
            "--set-cd-bit",
            "--set-do-bit",
            "--set-rd-bit",
            "--set-nsid-bit",
            "--protocol", "TCP",
            "--retry", "2",
            "--udp-payload-size", "5"
        ])
        self.assertEqual(
            self.cmd._get_measurement_kwargs(),
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
                "udp_payload_size": 5,
                "use_probe_resolver": False
            }
        )

    @mock.patch("ripe.atlas.tools.commands.measure.conf", Configuration.DEFAULT)
    def test_get_source_kwargs(self):

        spec = Configuration.DEFAULT["specification"]

        for kind in self.KINDS:

            tags = spec["tags"]["ipv{}".format(spec["af"])]
            includes = tags[kind]["include"] + tags["all"]["include"]
            excludes = tags[kind]["exclude"] + tags["all"]["exclude"]

            self.cmd.init_args([kind])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": spec["source"]["requested"],
                "type": spec["source"]["type"],
                "value": spec["source"]["value"],
                "tags": {"include": includes, "exclude": excludes}
            })

            self.cmd.init_args([
                kind,
                "--probes", "10",
                "--from-country", "ca"
            ])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": 10,
                "type": "country",
                "value": "CA",
                "tags": {"include": includes, "exclude": excludes}
            })

            for area in ("WW", "West", "North-Central", "South-Central",
                         "North-East", "South-East"):
                self.cmd.init_args([
                    kind,
                    "--probes", "10",
                    "--from-area", area
                ])
                self.assertEqual(self.cmd._get_source_kwargs(), {
                    "requested": 10,
                    "type": "area",
                    "value": area,
                    "tags": {"include": includes, "exclude": excludes}
                })

            self.cmd.init_args([
                kind,
                "--probes", "10",
                "--from-prefix", "1.2.3.0/22"
            ])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": 10,
                "type": "prefix",
                "value": "1.2.3.0/22",
                "tags": {"include": includes, "exclude": excludes}
            })

            self.cmd.init_args([
                kind,
                "--probes", "10",
                "--from-asn", "3333"
            ])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": 10,
                "type": "asn",
                "value": 3333,
                "tags": {"include": includes, "exclude": excludes}
            })

            # Try 20 permutations of probe lists
            for __ in range(0, 20):
                requested = randint(1, 500)
                selection = [str(randint(1, 5000)) for _ in range(0, 100)]
                self.cmd.init_args([
                    kind,
                    "--probes", str(requested),
                    "--from-probes", ",".join(selection)
                ])
                self.assertEqual(self.cmd._get_source_kwargs(), {
                    "requested": requested,
                    "type": "probes",
                    "value": ",".join(selection),
                    "tags": {"include": includes, "exclude": excludes}
                })

            self.cmd.init_args([
                kind,
                "--probes", "10",
                "--from-measurement", "1001"
            ])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": 10,
                "type": "msm",
                "value": 1001,
                "tags": {"include": includes, "exclude": excludes}
            })

            self.cmd.init_args([
                kind,
                "--include-tag", "tag-to-include",
                "--exclude-tag", "tag-to-exclude"
            ])
            self.assertEqual(self.cmd._get_source_kwargs(), {
                "requested": spec["source"]["requested"],
                "type": spec["source"]["type"],
                "value": spec["source"]["value"],
                "tags": {
                    "include": ["tag-to-include"],
                    "exclude": ["tag-to-exclude"]
                }
            })

    def test_get_af(self):

        conf = copy.deepcopy(Configuration.DEFAULT)
        conf["specification"]["af"] = 100

        with mock.patch(self.CONF, conf):
            for kind in self.KINDS:

                for af in (4, 6):
                    self.cmd.init_args([kind, "--af", str(af)])
                    self.assertEqual(self.cmd._get_af(), af)

                self.cmd.init_args([kind, "--target", "1.2.3.4"])
                self.assertEqual(self.cmd._get_af(), 4)

                self.cmd.init_args([kind, "--target", "1:2:3:4:5:6:7:8"])
                self.assertEqual(self.cmd._get_af(), 6)

                self.cmd.init_args([kind, "--target", "1.2.3.4.5"])
                self.assertEqual(
                    self.cmd._get_af(),
                    conf["specification"]["af"]
                )

    def test_handle_api_error(self):

        message = (
            "There was a problem communicating with the RIPE Atlas "
            "infrastructure.  The message given was:\n\n  {}"
        )

        with self.assertRaises(RipeAtlasToolsException) as e:
            self.cmd._handle_api_error("This is a plain text error")
        self.assertEqual(
            str(e.exception),
            message.format("This is a plain text error")
        )

        with self.assertRaises(RipeAtlasToolsException) as e:
            self.cmd._handle_api_error({"detail": "This is a formatted error"})
        self.assertEqual(
            str(e.exception),
            message.format("This is a formatted error")
        )

    def test_add_arguments(self):

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "not-a-type"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument type: invalid choice: "
                "'not-a-type' (choose from 'traceroute', 'ntp', 'ping', 'dns', "
                "'ssl')"
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "--renderer", "not-a-renderer"])
            self.assertTrue(stderr.getvalue().split("\n")[-2].startswith(
                "ripe-atlas measure: error: argument --renderer: invalid "
                "choice: 'not-a-renderer' (choose from"
            ))

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "--af", "5"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --af: invalid choice: 5 "
                "(choose from 4, 6)"
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "--target", "not a target"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --target: "
                "\"not a target\" does not appear to be an IP address or host "
                "name"
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "--from-area", "not an area"])
            self.assertTrue(stderr.getvalue().split("\n")[-2].startswith(
                "ripe-atlas measure: error: argument --from-area: invalid "
                "choice:"))

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["ping", "--from-probes", "0,50000"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --from-probes: 0 "
                "is lower than the minimum permitted value of 1."
            )

        for clude in ("in", "ex"):
            with capture_sys_output() as (stdout, stderr):
                for tag in ("NotATag", "tag!", "not a tag", "νοτ α ταγ"):
                    with self.assertRaises(SystemExit):
                        self.cmd.init_args([
                            "ping",
                            "--{}clude-tag".format(clude), tag
                        ])
                    self.assertEqual(
                        stderr.getvalue().split("\n")[-2],
                        'ripe-atlas measure: error: argument --{}clude-tag: '
                        '"{}" does not appear to be valid.'.format(clude, tag)
                    )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["traceroute", "--protocol", "invalid"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --protocol: invalid "
                "choice: 'invalid' (choose from 'ICMP', 'UDP', 'TCP')"
            )

        with capture_sys_output() as (stdout, stderr):
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["dns", "--protocol", "invalid"])
            self.assertEqual(
                stderr.getvalue().split("\n")[-2],
                "ripe-atlas measure: error: argument --protocol: invalid "
                "choice: 'invalid' (choose from 'UDP', 'TCP')"
            )

        min_options = {
            "from-measurement": 1,
            "probes": 1,
            "packets": 1,
            "size": 1,
            "packet-interval": 1,
            "timeout": 1,
            "destination-option-size": 1,
            "hop-by-hop-option-size": 1,
            "retry": 1,
            "udp-payload-size": 1
        }
        for option, minimum in min_options.items():
            with capture_sys_output() as (stdout, stderr):
                test_value = minimum - 1
                with self.assertRaises(SystemExit):
                    self.cmd.init_args(["--{}".format(option), str(test_value)])
                self.assertEqual(
                    stderr.getvalue().split("\n")[-2],
                    "ripe-atlas measure: error: argument --{}: "
                    "The integer must be greater than {}.".format(
                        option,
                        minimum
                    )
                )

        min_max_options = {
            "from-asn": (0, 2**32 + 1),
            "paris": (-1, 65),
            "first-hop": (0, 256),
            "max-hops": (0, 256),
            "port": (0, 2**16 + 1),
        }
        for option, extremes in min_max_options.items():
            for val in extremes:
                with capture_sys_output() as (stdout, stderr):
                    with self.assertRaises(SystemExit):
                        self.cmd.init_args(["--{}".format(option), str(val)])
                    self.assertEqual(
                        stderr.getvalue().split("\n")[-2],
                        "ripe-atlas measure: error: argument --{}: The "
                        "integer must be between {} and {}.".format(
                            option, extremes[0] + 1, extremes[1] - 1
                        )
                    )
