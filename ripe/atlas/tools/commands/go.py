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

import webbrowser
from .base import Command as BaseCommand
from ..helpers.validators import ArgumentType


class Command(BaseCommand):

    NAME = "go"

    DESCRIPTION = "Visit the web page for a specific measurement"
    URL = "https://atlas.ripe.net/measurements/{0}/"

    def add_arguments(self):
        self.parser.add_argument(
            "measurement_id",
            type=ArgumentType.msm_id_or_name(),
            help="The measurement id or alias you want reported"
        )

    def run(self):
        url = self.URL.format(self.arguments.measurement_id)
        if not webbrowser.open(url):
            self.ok(
                "It looks like your system doesn't have a web browser "
                "available.  You'll have to go there manually: {0}".format(url)
            )
