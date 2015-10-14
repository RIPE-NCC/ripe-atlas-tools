import sys


class Colour(object):

    @classmethod
    def _colourise(cls, t, c):
        return "{}[{}m{}{}[0m".format(chr(0x1b), c, t, chr(0x1b))

    @classmethod
    def black(cls, t):
        return cls._colourise(t, 30)

    @classmethod
    def red(cls, t):
        return cls._colourise(t, 31)

    @classmethod
    def green(cls, t):
        return cls._colourise(t, 32)

    @classmethod
    def yellow(cls, t):
        return cls._colourise(t, 33)

    @classmethod
    def blue(cls, t):
        return cls._colourise(t, 34)

    @classmethod
    def mangenta(cls, t):
        return cls._colourise(t, 35)

    @classmethod
    def cyan(cls, t):
        return cls._colourise(t, 36)

    @classmethod
    def white(cls,t):
        return cls._colourise(t, 37)

    @classmethod
    def bold(cls, t):
        return cls._colourise(t, 1)


def colourise(text, colour):
    if sys.stdout.isatty():
        return getattr(Colour, colour)(text)
    return text
