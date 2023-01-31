# Copyright (c) 2023 RIPE NCC
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

from typing import Optional
from datetime import datetime
import argparse
import importlib
import os
import pkgutil
import sys
import platform

from ..helpers.actions import StoreIfNotEmpty
from ..helpers import xdg
from ..helpers.colours import colourise
from ..version import __version__


class RipeHelpFormatter(argparse.RawTextHelpFormatter):
    def _format_usage(self, *args):
        r = argparse.RawTextHelpFormatter._format_usage(self, *args).capitalize()
        return "\n\n{}\n".format(r)


def _get_command_name(cmd_or_factory):
    return (
        cmd_or_factory.NAME
        if cmd_or_factory.NAME
        else cmd_or_factory.__module__.rsplit(".", 1)[-1]
    )


class Command(object):
    # If NAME isn't defined then the module name is used
    # It exists basically to allow hyphens in the command names
    NAME: Optional[str] = None
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
            description="\n\n".join(
                [
                    self.DESCRIPTION + ".",
                    getattr(self, "EXTRA_DESCRIPTION", ""),
                ]
            ),
            prog="ripe-atlas {}".format(self.get_name()),
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
        return os.path.join(xdg.get_config_home(), "commands")

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
            sys.stderr.write(
                colourise(
                    "Warning: {} is a deprecated alias for {}\n\n".format(
                        alias,
                        command_name,
                    ),
                    "yellow",
                )
            )

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

        self.arguments = self.parser.parse_args(self._modify_parser_args(args))

    def run(self):
        raise NotImplementedError()

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

    def print(self, message):
        """
        Write to stdout regardless of whether it is a tty or not.
        """
        sys.stdout.write(message + "\n")

    def ok(self, message):
        """
        Write a successful message to the tty if present.
        """
        if sys.stdout.isatty():
            sys.stdout.write("\n{}\n\n".format(colourise(message, "green")))

    def not_ok(self, message):
        """
        Writer an unsuccessful message to the tty if present.
        """
        if sys.stdout.isatty():
            sys.stdout.write("\n{}\n\n".format(colourise(message, "red")))

    @staticmethod
    def _get_os_string():
        """
        Return a string identifying the system OS suitable for use in the User-Agent
        header.
        """
        os = platform.system()

        if os == 'Darwin':
            release = platform.mac_ver()[0]
            return f'macOS {release}'
        elif os == 'Windows':
            release = platform.win32_ver()[0]
            return f"Windows {release}"
            pass
        else:
            try:
                # Use a shim for Python < 3.10
                info = xdg.freedesktop_os_release()
            except OSError:
                pass
            else:
                name = info.get("NAME")
                if name:
                    version = info.get("VERSION_ID", "")
                    return f"{name} {version}"
        return platform.platform()

    @classmethod
    def _get_user_agent(cls):
        """
        Allow packagers to change the user-agent to whatever they like by
        placing a file called `user-agent` into the `tools` directory.  If no
        file is found, we go with a sensible platform-specific default + the version.
        """

        try:
            custom = os.path.join(os.path.dirname(__file__), "..", "user-agent")
            with open(custom) as f:
                return f.readline().strip()[:128]
        except IOError:
            pass  # We go with the default

        os_str = cls._get_os_string()

        return f"RIPE Atlas Tools [{os_str}] {__version__}"

    def add_flag(self, parser, name, default, help, no_help=None):
        """
        Convenience method to create a store_true --foo option along with a --no-foo
        store_false counterpart, including proper indication of which is the default.

        This should be used when it's possible for a flag to have a True default,
        either in the defaults or the custom user YAML.
        """
        dest = name.replace("-", "_")

        if no_help is None:
            no_help = f"Do not {help[0].lower()}{help[1:]}"

        parser.set_defaults(**{dest: default})

        default_true = " (default)" if default else ""
        default_false = " (default)" if not default else ""

        parser.add_argument(
            f"--{name}",
            action="store_true",
            help=f"{help}{default_true}",
        )
        parser.add_argument(
            f"--no-{name}",
            action="store_false",
            dest=dest,
            help=f"{no_help}{default_false}",
        )

    def add_primary_argument(self, name, parser):
        """
        Create a positional argument which acts as an alias for --`name`.
        """
        parser.add_argument(
            name,
            help=f"If present, sets the --{name} argument",
            nargs="?",
            action=StoreIfNotEmpty,
        )


class MetaDataMixin(object):
    @staticmethod
    def _prettify_boolean(boolean):

        checkmark = "\u2714"
        x = "\u2718"

        if boolean:
            return colourise(checkmark, "green")
        return colourise(x, "red")

    @staticmethod
    def _prettify_time(dtime):
        if isinstance(dtime, datetime):
            return "{} UTC".format(dtime.isoformat().replace("T", " "))

        return str(dtime)

    @staticmethod
    def _render_line(header, value):
        print("{}  {}".format(colourise("{:25}".format(header), "bold"), value))


class Factory(object):
    NAME = None

    @classmethod
    def build(cls, *args, **kwargs):
        return object()

    @classmethod
    def get_name(cls):
        return _get_command_name(cls)
