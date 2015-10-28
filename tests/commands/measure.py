import unittest

# Python 3 comes with mock in unittest
try:
    from unittest import mock
except ImportError:
    import mock

from ripe.atlas.tools.commands.measure import Command
from ripe.atlas.tools.exceptions import RipeAtlasToolsException

from .. import capture_sys_output


class TestProbesCommand(unittest.TestCase):

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
                "DNS measurements require a query type, class, and argument"
            )

    def test_bad_type_argument(self):
        with capture_sys_output():
            with self.assertRaises(SystemExit):
                self.cmd.init_args(["not-a-type"])
