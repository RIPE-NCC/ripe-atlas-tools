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

import sys

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result

from .renderers import Renderer


class CaptureLimitExceeded(Exception):
    pass


class Stream(object):
    def __init__(self, capture_limit=None, timeout=None):

        self.num_results = 0
        self.capture_limit = capture_limit

        self.timeout = timeout

    def stream(self, renderer_name, arguments, kind, pk):
        cls = Renderer.get_renderer(name=renderer_name, kind=kind)
        renderer = cls(arguments=arguments)

        results = []

        def on_result_response(result, *args):
            parsed = Result.get(
                result,
                on_error=Result.ACTION_IGNORE,
                on_malformation=Result.ACTION_IGNORE,
            )
            if not results:
                print(renderer.header(sample=parsed))
            results.append(parsed)
            self.num_results += 1
            sys.stdout.write(renderer.on_result(parsed))
            if self.capture_limit and self.num_results >= self.capture_limit:
                raise CaptureLimitExceeded()

        stream = AtlasStream()
        stream.connect()

        stream.bind_channel("atlas_result", on_result_response)
        try:
            stream.start_stream(stream_type="result", msm=pk)
            stream.timeout(self.timeout)
        except (KeyboardInterrupt, CaptureLimitExceeded):
            stream.disconnect()
        finally:
            sys.stdout.write(renderer.footer(results={"": results}))
