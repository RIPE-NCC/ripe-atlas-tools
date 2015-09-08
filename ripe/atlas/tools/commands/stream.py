from __future__ import print_function, absolute_import
import json

from ripe.atlas.cousteau import AtlasRequest, AtlasStream
from ripe.atlas.sagan import Result, ResultError

from ..reports import Report
from .base import Command as BaseCommand


class Command(BaseCommand):

    DESCRIPTION = "Report the results of a measurement"
    URLS = {
        "detail": "/api/v2/measurements/{}.json",
        "latest": "/api/v2/measurements/{}/latest.json",
    }

    def __init__(self, *args, **kwargs):
        BaseCommand.__init__(self, *args, **kwargs)
        self.formatter = None

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=int,
            help="The measurement id you want streamed"
        )

    def run(self):

        pk = self.arguments.measurement_id

        detail = AtlasRequest(url_path=self.URLS["detail"].format(pk)).get()[1]

        self.formatter = Report.get_formatter(detail["type"]["name"])

        stream = AtlasStream()
        stream.connect()

        stream.bind_stream("result", self.on_result_response)
        try:
            stream.start_stream(stream_type="result", msm=pk)
            stream.timeout(seconds=None)
        except KeyboardInterrupt:
            self.ok("Disconnecting from the stream")
            stream.disconnect()


    def on_result_response(self, result, *args):
        print(self.formatter.format(Result.get(result)), end="")
