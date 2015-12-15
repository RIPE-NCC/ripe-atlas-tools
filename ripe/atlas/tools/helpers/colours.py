# Copyright (c) 2015 RIPE NCC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
