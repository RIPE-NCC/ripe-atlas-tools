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

from ripe.atlas.cousteau import Measurement, AtlasStream
from ripe.atlas.cousteau.exceptions import APIResponseError

from ..exceptions import RipeAtlasToolsException
from ..renderers import Renderer
from ..streaming import StreamWrapper
from ..helpers.validators import ArgumentType
from ..settings import conf
from .base import Command as BaseCommand


class Command(BaseCommand):

    NAME = "stream"

    DESCRIPTION = "Output the results of a public measurement as they become available"
    EXTRA_DESCRIPTION = "Streaming of non-public measurements is not supported."
    URLS = {
        "detail": "/api/v2/measurements/{0}.json",
    }

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=ArgumentType.msm_id_or_name(),
            help="The measurement id or alias you want streamed",
        )
        self.parser.add_argument(
            "--limit",
            type=int,
            help="The maximum number of results you want to stream",
        )
        self.parser.add_argument(
            "--renderer",
            choices=Renderer.get_available(),
            help="The renderer you want to use. If this isn't defined, an "
            "appropriate renderer will be selected.",
        )
        self.parser.add_argument(
            "--timeout",
            type=float,
            help="Stop streaming after this number of seconds",
        )
        self.parser.add_argument(
            "--send-backlog", action="store_true", help="Send backlog of recent results"
        )

        Renderer.add_arguments_for_available_renderers(self.parser)

    def run(self) -> None:
        try:
            measurement = Measurement(
                id=self.arguments.measurement_id,
                user_agent=self.user_agent,
            )
        except APIResponseError as e:
            raise RipeAtlasToolsException(e.args[0])

        self.ok("Connecting to stream...")
        stream = AtlasStream(base_url=conf["stream-base-url"])
        stream.connect()
        stream.subscribe(
            "result",
            msm=self.arguments.measurement_id,
            sendBacklog=self.arguments.send_backlog,
        )
        renderer = Renderer.get_renderer(
            name=self.arguments.renderer, kind=measurement.type.lower()
        )(arguments=self.arguments)
        renderer.render(
            StreamWrapper(
                stream,
                capture_limit=self.arguments.limit,
                timeout=self.arguments.timeout,
            )
        )
        self.ok("Disconnected from stream")
