from __future__ import print_function

import sys

from itertools import chain

from ripe.atlas.sagan import Result, ResultParseError

from ..helpers.validators import ArgumentType
from ..renderers import Renderer
from .base import Command as BaseCommand


class ResultPayload(object):
    """
    We need something that doesn't take up a lot of memory while it's being
    constructed, but that will also spread out into a handy string when we need
    it to.
    """

    def __init__(self, renderer=None, input=None, probes=()):
        self.renderer = renderer
        self.probes = probes
        self._input = input

    def __iter__(self):
        for line in self._input:
            if not line:
                break
            try:
                yield self.renderer.on_result(Result.get(
                    line,
                    on_error=Result.ACTION_IGNORE,
                    on_warning=Result.ACTION_IGNORE
                ), probes=self.probes)
            except ResultParseError:
                pass  # Probably garbage in the file

    def __next__(self):
        return iter(self).next()

    def next(self):
        return self.__next__()


class Rendering(object):

    def __init__(self, header="", footer="", payload=()):
        self.header = header
        self.footer = footer
        self.payload = payload

    def render(self):
        for line in chain(self.header, self.payload, self.footer):
            print(line, end="")


class Command(BaseCommand):

    NAME = "report"

    DESCRIPTION = "Render the contents of an arbitrary file.\n\nExample:\n" \
                  "  cat /my/file | ripe-atlas render\n"

    def add_arguments(self):
        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )
        self.parser.add_argument(
            "--probes",
            type=ArgumentType.comma_separated_integers,
            help="A comma-separated list of probe ids you want to see "
                 "exclusively."
        )
        self.parser.add_argument(
            "--from-file",
            type=ArgumentType.path,
            default="-",
            help='The source of the data to be rendered.  If nothing is '
                 'specified, we assume "-" or, standard in (the default).'
        )

    def run(self):

        using_regular_file = self.arguments.from_file != "-"

        renderer = Renderer.get_renderer(
            self.arguments.renderer, "ping")()

        source = sys.stdin
        if using_regular_file:
            source = open(self.arguments.from_file)

        payload = ResultPayload(renderer=renderer, input=source)

        Rendering(header="HEADER", footer="FOOTER", payload=payload).render()

        if using_regular_file:
            source.close()
