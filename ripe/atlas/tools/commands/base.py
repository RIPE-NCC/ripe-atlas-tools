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
import os
import re
import six
import sys

from datetime import datetime

from ..helpers.colours import colourise
from ..version import __version__


class RipeHelpFormatter(argparse.RawTextHelpFormatter):

    def _format_usage(self, *args):
        r = argparse.RawTextHelpFormatter._format_usage(
            self, *args).capitalize()
        return "\n\n{}\n".format(r)


class Command(object):

    NAME = ""
    DESCRIPTION = ""  # Define this in the subclass

    def __init__(self, *args, **kwargs):

        self.arguments = None
        self.parser = argparse.ArgumentParser(
            formatter_class=RipeHelpFormatter,
            description=self.DESCRIPTION,
            prog="ripe-atlas {}".format(self.NAME)
        )
        self.user_agent = self._get_user_agent()

    def init_args(self, args=None):
        """
        Initialises all parse arguments and makes them available to the class.
        """

        if args is None:
            args = sys.argv[1:]

        self.arguments = self.parser.parse_args(
            self._modify_parser_args(args))

    def run(self):
        raise NotImplemented()

    def add_arguments(self):
        """

        A hook that's executed in the __init__, you can make use of
        `self.parser` here to add arguments to the command:

          self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want to use"
          )

        """
        pass

    def _modify_parser_args(self, args):
        """
        A modifier hook that can be overridden in the child class to allow that
        class to manipulate the arguments before being parsed.  The common
        use-case we're trying to solve here is popping a secondary argument off
        of the list and/or appending `--help` in some circumstances.
        """

        self.add_arguments()

        return args

    def ok(self, message):
        sys.stdout.write("\n{}\n\n".format(colourise(message, "green")))

    @staticmethod
    def _get_user_agent():
        """
        Allow packagers to change the user-agent to whatever they like by
        placing a file called `user-agent` into the `tools` directory.  If no
        file is found, we go with a sensible default + the version.
        """

        try:
            custom = os.path.join(os.path.dirname(__file__), "..", "user-agent")
            with open(custom) as f:
                return f.readline().strip()[:128]
        except IOError:
            pass  # We go with the default

        return "RIPE Atlas Tools (Magellan) {}".format(__version__)


class TabularFieldsMixin(object):
    """
    A handy mixin to dump into classes that are expected to render tabular data.
    It expects both that COLUMNS is defined by the subclass and that --field is
    set in the add_arguments() method.
    """

    def _get_line_format(self):
        """
        Loop over the field arguments and generate a string that makes use of
        Python's string format mini language.  We later use this string to
        format the values for each row.
        """
        r = u""
        for field in self.arguments.field:
            if r:
                r += u" "
            r += (u"{!s:" + u"{}{}".format(*self.COLUMNS[field]) + u"}")
        return r

    def _get_header_names(self):
        return [_.capitalize() for _ in self.arguments.field]

    def _get_header(self):
        """
        Generates a header by using the line formatter and the list of field
        arguments.
        """
        return self._get_line_format().format(*self._get_header_names())

    def _get_horizontal_rule(self):
        """
        A bit of a hack: We get a formatted line for no other reason than to
        determine the width of that line.  Then we use a regex to overwrite that
        line with "=".
        """
        return re.sub(
            r".", "=", self._get_line_format().format(*self.arguments.field))

    def _get_line_items(self, measurement):
        raise NotImplementedError("This needs to be defined in the subclass.")

    def _get_filter_display(self, filters):

        if not filters:
            return ""

        r = colourise("\nFilters:\n", "white")
        for k, v in filters.items():
            if k not in ("search",):
                v = str(v).capitalize()
            r += colourise(
                "  {}: {}\n".format(*self._get_filter_key_value_pair(k, v)),
                "cyan"
            )

        return r

    def _get_filter_key_value_pair(self, k, v):
        return k.capitalize().replace("__", " "), v


class MetaDataMixin(object):

    @staticmethod
    def _prettify_boolean(boolean):

        checkmark = u"\u2714"
        x = u"\u2718"
        if six.PY2:
            checkmark = checkmark.encode("utf-8")
            x = x.encode("utf-8")

        if boolean:
            return colourise(checkmark, "green")
        return colourise(x, "red")

    @staticmethod
    def _prettify_time(timestamp):
        return "{} UTC".format(
            datetime.fromtimestamp(timestamp).isoformat().replace("T", " "))

    @staticmethod
    def _render_line(header, value):
        print("{}  {}".format(
            colourise("{:25}".format(header), "bold"), value))


class Factory(object):

    @classmethod
    def build(cls, *args, **kwargs):
        return object()
