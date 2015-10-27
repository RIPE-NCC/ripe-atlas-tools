from __future__ import absolute_import

import sys

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result

from .renderers import Renderer


class CaptureLimitExceeded(Exception):
    pass


class Stream(object):

    def __init__(self, capture_limit=None, timeout=None):

        self.captured = 0
        self.capture_limit = capture_limit

        self.timeout = timeout

    def stream(self, renderer_name, kind, pk):

        renderer = Renderer.get_renderer(name=renderer_name, kind=kind)()

        def on_result_response(result, *args):
            sys.stdout.write(renderer.on_result(Result.get(
                result,
                on_error=Result.ACTION_IGNORE,
                on_malformation=Result.ACTION_IGNORE
            )))
            self.captured += 1
            if self.capture_limit and self.captured >= self.capture_limit:
                raise CaptureLimitExceeded()

        stream = AtlasStream()
        stream.connect()

        stream.bind_stream("result", on_result_response)
        try:
            stream.start_stream(stream_type="result", msm=pk)
            stream.timeout(self.timeout)
        except (KeyboardInterrupt, CaptureLimitExceeded) as e:
            stream.disconnect()
            raise e
