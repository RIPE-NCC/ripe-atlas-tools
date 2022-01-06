# Copyright (c) 2016 RIPE NCC
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
import os
import re
import sys

from dateutil import parser

from ..settings import aliases


class ArgumentType(object):
    @staticmethod
    def path(string):
        if not os.path.exists(string) and not string == "-":
            raise argparse.ArgumentTypeError(
                'The file name specified, "{}" does not appear to exist'.format(string)
            )
        return string

    @staticmethod
    def country_code(string):
        if not re.match(r"^[a-zA-Z][a-zA-Z]$", string):
            raise argparse.ArgumentTypeError(
                "Countries must be defined with a two-letter ISO code"
            )
        return string.upper()

    @staticmethod
    def datetime(string):
        try:
            return parser.parse(string)
        except parser.ParserError:
            raise argparse.ArgumentTypeError(
                "Times must be specified in ISO 8601 format.  For example: "
                "2010-10-01T00:00:00 or a portion thereof.  All times are in "
                "UTC."
            )

    @staticmethod
    def ip_or_domain(string):
        message = '"{}" does not appear to be an IP address or host ' "name".format(
            string
        )

        if " " in string:
            raise argparse.ArgumentTypeError(message)
        if "." not in string and ":" not in string:
            if not re.match(r"^\w+$", string):
                raise argparse.ArgumentTypeError(message)

        return string

    @classmethod
    def comma_separated_integers_or_file(cls, string):
        """
        Allow a list of comma-separated integers, or a file containing a
        newline-separated list of integers, OR "-" which implies standard out.
        """

        if re.match(r"^((\d+,?)+)$", string):
            return cls.comma_separated_integers()(string)

        f = sys.stdin
        if not string == "-":
            if not os.path.exists(string):
                raise argparse.ArgumentTypeError("Cannot find file: {}".format(string))
            f = open(string)

        try:
            return [int(_) for _ in f.readlines()]
        except ValueError:
            raise argparse.ArgumentTypeError(
                "The contents of the file presented does not conform to input "
                "standards.  Please ensure that every line in the file "
                "consists of a single integer."
            )

    @staticmethod
    def tag(string):
        pattern = re.compile(r"^[a-z_\-0-9]+$")

        if not pattern.match(string):
            raise argparse.ArgumentTypeError(
                '"{}" does not appear to be a valid tag.'.format(string)
            )

        return string

    class integer_range(object):
        def __init__(self, minimum=float("-inf"), maximum=float("inf")):
            self.minimum = minimum
            self.maximum = maximum

        def __call__(self, string):

            message = "The integer must be between {} and {}.".format(
                self.minimum, self.maximum
            )
            if self.maximum == float("inf"):
                message = "The integer must be greater than {}.".format(self.minimum)

            try:
                integer = int(string)
                if integer < self.minimum or integer > self.maximum:
                    raise argparse.ArgumentTypeError(message)
            except ValueError:
                raise argparse.ArgumentTypeError("An integer must be specified.")

            return integer

    class comma_separated_integers(object):
        def __init__(self, minimum=float("-inf"), maximum=float("inf")):
            self.minimum = minimum
            self.maximum = maximum

        def __call__(self, string):

            r = []

            for i in string.split(","):

                try:
                    i = int(i)
                except ValueError:
                    raise argparse.ArgumentTypeError(
                        "The ids supplied were not in the correct format. Note "
                        "that you must specify them as a list of "
                        "comma-separated integers without spaces.  Example: "
                        "1,2,34,157,10006"
                    )

                if i < self.minimum:
                    raise argparse.ArgumentTypeError(
                        "{} is lower than the minimum permitted value of "
                        "{}.".format(i, self.minimum)
                    )
                if i > self.maximum:
                    raise argparse.ArgumentTypeError(
                        "{} exceeds the maximum permitted value of {}.".format(
                            i, self.maximum
                        )
                    )

                r.append(i)

            return r

    class regex(object):
        def __init__(self, regex):
            self.regex = re.compile(regex)

        def __call__(self, string):

            if not self.regex.match(string):
                raise argparse.ArgumentTypeError(
                    '"{}" does not appear to be valid.'.format(string)
                )

            return string

    @staticmethod
    def alias_is_valid(string):
        ret = None

        if string and not string.isdigit():
            pattern = re.compile(r"^[a-zA-Z\._\-0-9]+$")

            if pattern.match(string):
                ret = string

        if not ret:
            raise argparse.ArgumentTypeError(
                '"{}" does not appear to be a valid ' "alias.".format(string)
            )

        return ret

    class id_or_alias(object):
        TYPE = None

        def __call__(self, string):
            if string.isdigit():
                return int(string)

            if string in aliases[self.TYPE]:
                return int(aliases[self.TYPE][string])
            else:
                raise argparse.ArgumentTypeError(
                    '"{}" does not appear to be an existent '
                    "{} alias.".format(string, self.TYPE)
                )

    class msm_id_or_name(id_or_alias):
        TYPE = "measurement"

    class probe_id_or_name(id_or_alias):
        TYPE = "probe"
