import argparse


class Command(object):

    DESCRIPTION = ""

    def __init__(self, sys_args):

        self.parser = argparse.ArgumentParser(description=self.DESCRIPTION)

        self.add_arguments()

        self.arguments = self.parser.parse_args()

    def run(self):
        raise NotImplemented()

    def add_arguments(self):
        pass
