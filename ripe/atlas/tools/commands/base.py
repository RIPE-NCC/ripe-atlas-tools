import argparse
import sys

from ..helpers.colours import Colour


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
            message = Colour.green + message + Colour.reset
        sys.stdout.write("\n{0}\n\n".format(message))
