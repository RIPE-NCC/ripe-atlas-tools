from __future__ import print_function, absolute_import

from ripe.atlas.cousteau import Measurement, APIResponseError

from ..exceptions import RipeAtlasToolsException
from ..renderers import Renderer
from ..streaming import Stream, CaptureLimitExceeded
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "stream"

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{0}.json",
    }

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
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

        try:
            measurement = Measurement(id=self.arguments.measurement_id)
        except APIResponseError:
            raise RipeAtlasToolsException("That measurement does not exist")

        try:
            Stream(capture_limit=self.arguments.limit).stream(
                self.arguments.renderer,
                measurement.type.lower(),
                self.arguments.measurement_id
            )
        except (KeyboardInterrupt, CaptureLimitExceeded):
            self.ok("Disconnecting from the stream")
