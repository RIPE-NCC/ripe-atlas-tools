from __future__ import print_function, absolute_import

import argparse
from dateutil import parser
import os
import re


class ArgumentType(object):

    @staticmethod
    def path(string):
        if not os.path.exists(string) and not string == "-":
            raise argparse.ArgumentTypeError(
                'The file name specified, "{}" does not appear to exist'.format(
                    string
                )
            )
        return string

    @staticmethod
    def country_code(string):
        if not re.match(r"^[a-zA-Z][a-zA-Z]$", string):
            raise argparse.ArgumentTypeError(
                "Countries must be defined with a two-letter ISO code")
        return string.upper()

    @staticmethod
    def comma_separated_integers(string):
        try:
            return [int(_) for _ in string.split(",")]
        except ValueError:
            raise argparse.ArgumentTypeError(
                "The ids supplied were not in the correct format. Note "
                "that you must specify them as a list of comma-separated "
                "integers without spaces.  Example: 1,2,34,157,10006"
            )

    @staticmethod
    def datetime(string):
        try:
            return parser.parse(string)
        except:
            raise argparse.ArgumentTypeError(
                "Times must be specified in ISO 8601 format.  For example: "
                "2010-10-01T00:00:00 or a portion thereof.  All times are in "
                "UTC."
            )
