# Copyright (c) 2016 RIPE NCC
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
import time

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result


class CaptureLimitExceeded(Exception):
    pass


class Stream(object):
    """
    Iterable wrapper for AtlasStream that yields sagan Results up to a
    specified capture limit.
    """

    STREAM_INTERVAL = 0.01

    def __init__(self, pk, capture_limit=None, timeout=None):
        self.pk = pk
        self.capture_limit = capture_limit
        self.timeout = timeout

        self.num_results = 0

    def __iter__(self):
        results = []

        def on_result_response(result, *args):
            parsed = Result.get(
                result,
                on_error=Result.ACTION_IGNORE,
                on_malformation=Result.ACTION_IGNORE,
            )
            results.append(parsed)

        stream = AtlasStream()
        stream.connect()

        start = time.time()
        remaining = self.timeout

        stream.bind_channel("atlas_result", on_result_response)
        stream.start_stream(stream_type="result", msm=self.pk)
        try:
            while self.timeout is None or remaining > self.STREAM_INTERVAL:
                stream.timeout(self.STREAM_INTERVAL)
                for result in results:
                    self.num_results += 1
                    if self.capture_limit and self.num_results > self.capture_limit:
                        raise CaptureLimitExceeded()
                    yield result
                results = []
                if self.timeout is not None:
                    remaining = start + self.timeout - time.time()
        except (KeyboardInterrupt, CaptureLimitExceeded):
            stream.disconnect()
