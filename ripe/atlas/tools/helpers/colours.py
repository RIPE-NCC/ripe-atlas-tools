import sys


class Colour(object):

    @classmethod
    def _colourise(cls, text, colour):
        return "{}[{}m{}{}[0m".format(chr(0x1b), colour, text, chr(0x1b))

    @classmethod
    def black(cls, text):
        return cls._colourise(text, 30)

    @classmethod
    def red(cls, text):
        return cls._colourise(text, 31)

    @classmethod
    def green(cls, text):
        return cls._colourise(text, 32)

    @classmethod
    def yellow(cls, text):
        return cls._colourise(text, 33)

    @classmethod
    def blue(cls, text):
        return cls._colourise(text, 34)

    @classmethod
    def mangenta(cls, text):
        return cls._colourise(text, 35)

    @classmethod
    def cyan(cls, text):
        return cls._colourise(text, 36)

    @classmethod
    def white(cls, text):
        return cls._colourise(text, 37)

    @classmethod
    def bold(cls, text):
        return cls._colourise(text, 1)


def colourise(text, colour):
    if sys.stdout.isatty():
        return getattr(Colour, colour)(text)
    return text
