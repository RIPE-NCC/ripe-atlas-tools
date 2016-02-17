# Copyright (c) 2015 RIPE NCC
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

from __future__ import print_function, absolute_import

from ripe.atlas.cousteau import Measurement
from ripe.atlas.cousteau.exceptions import APIResponseError

from ..exceptions import RipeAtlasToolsException
from ..renderers import Renderer
from ..streaming import Stream, CaptureLimitExceeded
from .base import Command as BaseCommand
from ..settings import conf


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
            "--auth",
            type=str,
            choices=conf["authorisation"]["fetch_aliases"].keys(),
            default=conf["authorisation"]["fetch"],
            help="The API key alias you want to use to fetch the measurement. "
                 "To configure an API key alias, use "
                 "ripe-atlas configure --set authorisation.fetch_aliases."
                 "ALIAS_NAME=YOUR_KEY"

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

    def _get_request_auth(self):
        if self.arguments.auth:
            return conf["authorisation"]["fetch_aliases"][self.arguments.auth]
        else:
            return conf["authorisation"]["fetch"]

    def run(self):

        try:
            measurement = Measurement(
                id=self.arguments.measurement_id, user_agent=self.user_agent,
                key=self._get_request_auth)
        except APIResponseError as e:
            raise RipeAtlasToolsException(e.args[0])

        try:
            Stream(capture_limit=self.arguments.limit).stream(
                self.arguments.renderer,
                measurement.type.lower(),
                self.arguments.measurement_id
            )
        except (KeyboardInterrupt, CaptureLimitExceeded):
            self.ok("Disconnecting from the stream")
