from __future__ import absolute_import

import sys

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result

from .reports import Report


class CaptureLimitExceeded(Exception):
    pass


class Stream(object):

    def __init__(self, capture_limit=None):
        self.captured = 0
        self.capture_limit = capture_limit

    def stream(self, kind, pk):

        formatter = Report.get_formatter(kind)

        def on_result_response(result, *args):
            sys.stdout.write(formatter.format(Result.get(result)))
            self.captured += 1
            if self.capture_limit and self.captured >= self.capture_limit:
                raise CaptureLimitExceeded()

        stream = AtlasStream()
        stream.connect()

        stream.bind_stream("result", on_result_response)
        try:
            stream.start_stream(stream_type="result", msm=pk)
            stream.timeout()
        except (KeyboardInterrupt, CaptureLimitExceeded), e:
            stream.disconnect()
            raise e
