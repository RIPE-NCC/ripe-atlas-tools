from __future__ import print_function, absolute_import

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result

from .reports import Report


class Stream(object):

    @staticmethod
    def stream(kind, pk):

        formatter = Report.get_formatter(kind)

        def on_result_response(result, *args):
            print(formatter.format(Result.get(result)), end="")

        stream = AtlasStream()
        stream.connect()

        stream.bind_stream("result", on_result_response)
        try:
            stream.start_stream(stream_type="result", msm=pk)
            stream.timeout()
        except KeyboardInterrupt, e:
            stream.disconnect()
            raise e
