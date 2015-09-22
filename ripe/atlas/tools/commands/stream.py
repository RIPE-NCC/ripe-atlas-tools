from __future__ import print_function, absolute_import

from ripe.atlas.cousteau import AtlasRequest

from ..renderers import Renderer
from ..streaming import Stream, CaptureLimitExceeded
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{0}.json",
    }

    NAME = "stream"

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self.formatter = None

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            nargs='?',
            help="The measurement id you want streamed"
        )
        self.parser.add_argument(
            "--limit",
            type=int,
            help="The maximum number of results you want to stream"
        )
        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
                 "appropriate renderer will be selected."
        )

    def run(self):

        pk = self.arguments.measurement_id

        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]

        try:
            Stream(capture_limit=self.arguments.limit).stream(
                self.arguments.renderer,
                detail["type"]["name"],
                pk
            )
        except (KeyboardInterrupt, CaptureLimitExceeded):
            self.ok("Disconnecting from the stream")
