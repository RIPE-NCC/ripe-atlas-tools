import argparse


class Command(object):

    DESCRIPTION = ""  # Define this in the subclass

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
