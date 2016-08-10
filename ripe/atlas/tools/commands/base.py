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

from datetime import datetime
import argparse
import importlib
import os
import pkgutil
import re
import six
import sys

from ..helpers.colours import colourise
from ..version import __version__


class RipeHelpFormatter(argparse.RawTextHelpFormatter):

    def _format_usage(self, *args):
        r = argparse.RawTextHelpFormatter._format_usage(
            self, *args).capitalize()
        return "\n\n{}\n".format(r)


def _get_command_name(cmd_or_factory):
    return cmd_or_factory.NAME if cmd_or_factory.NAME else \
        cmd_or_factory.__module__.rsplit(".", 1)[-1]


class Command(object):
    # If NAME isn't defined then the module name is used
    # It exists basically to allow hyphens in the command names
    NAME = None
    DESCRIPTION = ""  # Define this in the subclass
    _commands = None

    DEPRECATED_ALIASES = {
        "measurement": "measurement-info",
        "measurements": "measurement-search",
        "probe": "probe-info",
        "probes": "probe-search",
        "render": "report",
    }

    def __init__(self, *args, **kwargs):

        self.arguments = None
        self.parser = argparse.ArgumentParser(
            formatter_class=RipeHelpFormatter,
            description="\n\n".join([
                self.DESCRIPTION + ".",
                getattr(self, "EXTRA_DESCRIPTION", ""),
            ]),
            prog="ripe-atlas {}".format(self.get_name())
        )
        self.user_agent = self._get_user_agent()

    @classmethod
    def get_name(cls):
        return _get_command_name(cls)

    @staticmethod
    def _get_packages_for_paths(paths):
        """
        Yield path, package_name for all of the packages found in `paths`.
        """
        for loader, package_name, _ in pkgutil.iter_modules(paths):
            yield loader.path, package_name

    @classmethod
    def _get_user_command_path(cls):
        user_base_path = os.path.join(
            os.path.expanduser("~"), ".config", "ripe-atlas-tools",
        )
        return os.path.join(user_base_path, "commands")

    @classmethod
    def _load_commands(cls):
        """
        Scan for available commands and store a map of command names to module
        paths.
        """
        builtin_path = os.path.dirname(__file__)
        user_command_path = cls._get_user_command_path()

        cls._commands = {}

        paths = [builtin_path, user_command_path]
        for path, package_name in cls._get_packages_for_paths(paths):
            if package_name == "base":
                continue
            if path == builtin_path:
                module = "ripe.atlas.tools.commands.{}".format(package_name)
            else:
                module = package_name
                if user_command_path not in sys.path:
                    sys.path.append(user_command_path)
            cls._commands[package_name] = module

    @classmethod
    def load_command_class(cls, command_name):
        """
        Get the Command or Factory with the given command name.
        """
        if command_name in cls.DEPRECATED_ALIASES:
            alias = command_name
            command_name = cls.DEPRECATED_ALIASES[alias]
            sys.stderr.write(colourise(
                "Warning: {} is a deprecated alias for {}\n\n".format(
                    alias, command_name,
                ),
                "yellow"
            ))

        if cls._commands is None:
            cls._load_commands()

        try:
            module_name = cls._commands[command_name.replace("-", "_")]
        except KeyError:
            return

        module = importlib.import_module(module_name)

        if hasattr(module, "Factory"):
            cmd = module.Factory
        else:
            cmd = module.Command

        return cmd

    @classmethod
    def get_available_commands(cls):
        """
        Get a list of commands that we can execute.  By default, we have a
        fixed list that we make available in this directory, but the user can
        create her own plugins and store them at
        ~/.config/ripe-atlas-tools/commands/.  If we find any files there, we
        add them to the list here.
        """
        if not cls._commands:
            cls._load_commands()

        return sorted(cls._commands.keys())

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
        if sys.stdout.isatty():
            sys.stdout.write("\n{}\n\n".format(colourise(message, "green")))

    def not_ok(self, message):
        if sys.stdout.isatty():
            sys.stdout.write("\n{}\n\n".format(colourise(message, "red")))

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
    def _prettify_time(dtime):
        if isinstance(dtime, datetime):
            return "{} UTC".format(
                dtime.isoformat().replace("T", " "))

        return str(dtime)

    @staticmethod
    def _render_line(header, value):
        print("{}  {}".format(
            colourise("{:25}".format(header), "bold"), value))


class Factory(object):
    NAME = None

    @classmethod
    def build(cls, *args, **kwargs):
        return object()

    @classmethod
    def get_name(cls):
        return _get_command_name(cls)
