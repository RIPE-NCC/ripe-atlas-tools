# Copyright (c) 2023 RIPE NCC
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

from typing import Iterator, Optional

from ripe.atlas.cousteau import AtlasStream
from ripe.atlas.sagan import Result


class StreamWrapper:
    """
    Iterable wrapper for AtlasStream that yields sagan Results up to a
    specified capture limit and/or timeout
    """

    def __init__(
        self,
        stream: AtlasStream,
        capture_limit: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> None:
        self.stream = stream
        self.capture_limit = capture_limit
        self.timeout = timeout
        self.num_received = 0

    def __iter__(self) -> Iterator[Result]:
        for event_name, payload in self.stream.iter(seconds=self.timeout):
            if event_name == "atlas_result":
                parsed = Result.get(
                    payload,
                    on_error=Result.ACTION_IGNORE,
                    on_malformation=Result.ACTION_IGNORE,
                )
                yield parsed
                self.num_received += 1
                if self.num_received == self.capture_limit:
                    break
