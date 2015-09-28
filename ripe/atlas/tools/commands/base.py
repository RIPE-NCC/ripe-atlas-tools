import argparse
import sys


class Command(object):

    NAME = ""
    DESCRIPTION = ""  # Define this in the subclass
    COLOURS = {
        "light-blue": "\033[1;34m",
        "light-green": "\033[1;32m",
        "light-cyan": "\033[1;36m",
        "light-red": "\033[1;31m",
        "yellow": "\033[1;33m",
        "green": "\033[0;32m",
        "cyan": "\033[0;36m",
        "brown": "\033[0;33m",
        "pink": "\033[1;35m",
        "reset": "\033[0m"
    }

    def __init__(self, *args, **kwargs):

        self.arguments = None
        self.parser = argparse.ArgumentParser(
            description=self.DESCRIPTION,
            prog="ripe-atlas {0}".format(self.NAME)
        )

        self.add_arguments()

    def init_args(self, parser_args=None):
        """
        Initialises all parse arguments and makes them available to class.
        """

        if parser_args is None:
            self.arguments = self.parser.parse_args()
        else:
            self.arguments = self.parser.parse_args(parser_args)

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

    def ok(self, message):
        if sys.stdout.isatty():
            message = self.COLOURS["green"] + message + self.COLOURS["reset"]
        sys.stdout.write("\n{0}\n\n".format(message))
