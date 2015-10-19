import functools
import os

from ..exceptions import RipeAtlasToolsException
from ..settings import Configuration, conf
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "configure"

    EDITOR = os.environ.get("EDITOR", "/usr/bin/vim")
    DESCRIPTION = "An easy way to configure this tool. Alternatively, you " \
                  "can always just create/edit {}".format(Configuration.USER_RC)

    def add_arguments(self):
        self.parser.add_argument(
            "--editor",
            action="store_true",
            help="Invoke {0} to edit the configuration directly".format(
                self.EDITOR)
        )
        self.parser.add_argument(
            "--set",
            action="store",
            help="Permanently set a configuration value so it can be used in "
                 "the future.  Example: --set authorisation.create=MY_API_KEY"
        )
        self.parser.add_argument(
            "--init",
            action="store_true",
            help="Create a configuration file and save it into your home "
                 "directory at: {}".format(Configuration.USER_RC)
        )

    def run(self):

        if not self.arguments.init:
            if not self.arguments.editor:
                if not self.arguments.set:
                    raise RipeAtlasToolsException(
                        "Run this with --help for more information")

        self._create_if_necessary()

        if self.arguments.editor:
            os.system("{0} {1}".format(self.EDITOR, Configuration.USER_RC))

        if self.arguments.init or self.arguments.editor:
            return self.ok(
                "Configuration file writen to {}".format(Configuration.USER_RC))

        if self.arguments.set:
            if "=" not in self.arguments.set:
                raise RipeAtlasToolsException(
                    "Invalid format. Execute with --help for more information.")
            path, value = self.arguments.set.split("=")
            self.set(path.split("."), value)

    def set(self, path, value):

        try:
            required_type = type(self._get_from_dict(conf, path))
        except KeyError:
            raise RipeAtlasToolsException(
                'Invalid configuration key: "{}"'.format(".".join(path)))

        if value.isdigit():
            value = int(value)

        if not isinstance(value, required_type):
            raise RipeAtlasToolsException(
                'Invalid configuration value: "{}". You must supply a {} for '
                'this key'.format(value, required_type.__name__)
            )

        self._set_in_dict(conf, path, value)

        Configuration.write(conf)

    @staticmethod
    def _create_if_necessary():

        if os.path.exists(Configuration.USER_RC):
            return

        if not os.path.exists(Configuration.USER_CONFIG_DIR):
            os.makedirs(Configuration.USER_CONFIG_DIR)

        Configuration.write(conf)

    @staticmethod
    def _get_from_dict(data, path):
        return functools.reduce(lambda d, k: d[k], path, data)

    @classmethod
    def _set_in_dict(cls, data, path, value):
        cls._get_from_dict(data, path[:-1])[path[-1]] = value

    @staticmethod
    def cast_value(value):

        # Booleans are a pain in the ass to cast
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return str(value)
