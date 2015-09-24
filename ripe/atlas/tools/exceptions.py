import sys


class RipeAtlasToolsException(Exception):

    RED = "\033[1;31m"
    RESET = "\033[0m"

    def write(self):
        r = str(self)
        if sys.stderr.isatty():
            r = self.RED + r + self.RESET
        sys.stderr.write("\n{0}\n\n".format(r))
