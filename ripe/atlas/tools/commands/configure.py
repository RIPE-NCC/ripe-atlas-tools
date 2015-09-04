import os
import yaml

from ..settings import Configuration, conf
from .base import Command as BaseCommand


class Command(BaseCommand):

    EDITOR = os.environ.get("EDITOR", "/usr/bin/vim")
    DESCRIPTION = "An easy way to configure this tool.  Alternatively, you " \
                  "can always just create/edit {}".format(Configuration.USER_RC)

    def add_arguments(self):
        self.parser.add_argument(
            "--editor",
            action="store_true",
            help="Invoke {} to edit the configuration directly".format(
                self.EDITOR
            )
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
            help="Create a configuration file and save it into your home directory at: {}".format(
                Configuration.USER_RC)
        )

    def run(self):

        if self.arguments.init or self.arguments.editor or self.arguments.set:

            self._create_if_necessary()

        if self.arguments.editor:
            os.system("{} {}".format(self.EDITOR, Configuration.USER_RC))

        if self.arguments.init or self.arguments.editor:
            return self.ok(
                "Configuration file writen to {}".format(Configuration.USER_RC))

        if self.arguments.set:
            print(self.arguments.set)

    @staticmethod
    def _create_if_necessary():

        if os.path.exists(Configuration.USER_RC):
            return

        os.makedirs(Configuration.USER_CONFIG_DIR)
        template = os.path.join(
            os.path.dirname(__file__),
            "..",
            "settings",
            "templates",
            "base.yaml"
        )
        with open(Configuration.USER_RC, "w") as rc:
            with open(template) as t:
                rc.write(t.read().format(
                    authorisation=yaml.dump(
                        conf["authorisation"], default_flow_style=False),
                    create=yaml.dump(conf["create"], default_flow_style=False)
                ))
