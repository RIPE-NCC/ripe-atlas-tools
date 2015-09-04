import sys


class RipeAtlasToolsException(Exception):

    RED = "\033[1;31m"
    RESET = "\033[0m"

    def write(self):
        sys.stderr.write("\n" + self.RED + str(self) + self.RESET + "\n\n")
