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

import argparse
import datetime
import os
import sys
import unittest

try:
    from cStringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO

from ripe.atlas.tools.helpers.validators import ArgumentType


class TestArgumentTypeHelper(unittest.TestCase):

    def test_path(self):

        self.assertEqual("/tmp", ArgumentType.path("/tmp"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.path("/not/a/real/place")

    def test_country_code(self):

        self.assertEqual("CA", ArgumentType.country_code("CA"))
        self.assertEqual("CA", ArgumentType.country_code("ca"))
        self.assertEqual("CA", ArgumentType.country_code("Ca"))
        self.assertEqual("CA", ArgumentType.country_code("cA"))

        for value in ("CAN", "Canada", "can", "This isn't even a country"):
            with self.assertRaises(argparse.ArgumentTypeError):
                ArgumentType.country_code(value)

    def test_comma_separated_integers(self):

        self.assertEqual(
            [1, 2, 3], ArgumentType.comma_separated_integers()("1,2,3"))

        self.assertEqual(
            [1, 2, 3], ArgumentType.comma_separated_integers()("1, 2, 3"))

        self.assertEqual([1], ArgumentType.comma_separated_integers()("1"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers()("1,2,3,pizza!")
        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers(minimum=5)("4,5,6,7")
        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers(maximum=5)("1,2,3,4,6")

    def test_datetime(self):

        d = datetime.datetime(2015, 12, 1)

        self.assertEqual(d, ArgumentType.datetime("2015-12-1"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1T00:00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00:00"))
        self.assertEqual(d, ArgumentType.datetime("2015-12-1 00:00:00"))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.datetime("yesterday")

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.datetime("Definitely not a date, or even a time")

    def test_integer_range(self):

        self.assertEqual(1, ArgumentType.integer_range(1, 10)("1"))
        self.assertEqual(10, ArgumentType.integer_range(1, 10)("10"))
        self.assertEqual(1, ArgumentType.integer_range(-1, 1)("1"))
        self.assertEqual(-1, ArgumentType.integer_range(-1, 1)("-1"))

        for value in ("0", "11", "-1"):
            with self.assertRaises(argparse.ArgumentTypeError):
                ArgumentType.integer_range(1, 10)(value)

    def test_ip_or_domain(self):

        passable_hosts = (
            "localhost", "ripe.net", "www.ripe.net", "1.2.3.4",
            "2001:67c:2e8:22::c100:68b"
        )
        for host in passable_hosts:
            self.assertEqual(host, ArgumentType.ip_or_domain(host))

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.ip_or_domain("Definitely not a host")

    def test_comma_separated_integers_or_file(self):

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers_or_file("/dev/null/fail")

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers_or_file("not,a,number")

        with self.assertRaises(argparse.ArgumentTypeError):
            ArgumentType.comma_separated_integers_or_file("1, 2, 3")

        old = sys.stdin
        sys.stdin = StringIO("1\n2\n")
        self.assertEqual(
            ArgumentType.comma_separated_integers_or_file("-"),
            [1, 2]
        )
        sys.stdin = old

        in_file = "/tmp/__test_file__"
        with open(in_file, "w") as f:
            f.write("1\n2\n3\n")
        self.assertEqual(
            ArgumentType.comma_separated_integers_or_file(in_file),
            [1, 2, 3]
        )
        os.unlink(in_file)

    def test_measurement_alias(self):

        tests = ["", "\\invalid", "+invalid",
                 ":invalid", "12345"]
        for test in tests:
            with self.assertRaises(argparse.ArgumentTypeError):
                ArgumentType.alias_is_valid(test)

        tests = ["valid", "123valid", "valid123", "_valid",
                 "valid_", "-valid", "valid-", ".valid"]

        for test in tests:
            self.assertEqual(
                ArgumentType.alias_is_valid(test),
                test
            )
