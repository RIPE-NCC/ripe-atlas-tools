import argparse
import sys


class Command(object):

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

        self.parser = argparse.ArgumentParser(description=self.DESCRIPTION)

        self.add_arguments()

        self.arguments = self.parser.parse_args()

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
        sys.stdout.write("\n{}{}{}\n\n".format(
            self.COLOURS["green"], message, self.COLOURS["reset"]))
