from __future__ import print_function, absolute_import

import argparse
import re


class ArgumentType(object):

    @staticmethod
    def country_code(string):
        if not re.match(r"^[a-zA-Z][a-zA-Z]$", string):
            raise argparse.ArgumentTypeError(
                "Countries must be defined with a two-letter ISO code")
        return string.upper()

    @staticmethod
    def comma_separated_integers(string):
        for probe_id in string.split(","):
            if not probe_id.isdigit():
                raise argparse.ArgumentTypeError(
                    "The ids supplied were not in the correct format. Note that"
                    "you must specify them as a list of comma-separated "
                    "integers without spaces.  Example: 1,2,34,157,10006"
                )
        return string


