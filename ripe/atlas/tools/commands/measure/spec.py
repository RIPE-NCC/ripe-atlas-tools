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
import json

from .base import Command
from ...settings import conf
from ...exceptions import RipeAtlasToolsException


class SpecMeasureCommand(Command):
    DESCRIPTION = "Create a measurement from a JSON spec and wait for the results"

    def clean_target(self):
        return self.arguments.target

    def add_arguments(self):

        Command.add_arguments(self)

        self.parser.add_argument(
            "json_spec",
            help="JSON object containing the RIPE Atlas measurement spec. "
            "Use @some-file.json to load the spec from a given file, or @- to load the "
            "spec from standard input. "
            "Any optional command-line arguments you specify will be merged into this "
            "spec.",
        )
        self.parser.add_argument(
            "--type",
            help="The 'type' of the measurement to be added to the spec JSON",
        )

    def _read_file(self, filename):
        if filename == "-":
            return sys.stdin.read()
        try:
            with open(filename) as f:
                return f.read()
        except FileNotFoundError:
            raise RipeAtlasToolsException(f"No such file: {filename}")

    def _clean_json_spec(self):
        arg = self.arguments.json_spec
        if arg.startswith("@"):
            arg = self._read_file(arg[1:])

        try:
            spec = json.loads(arg)
        except ValueError:
            raise RipeAtlasToolsException("Spec is invalid JSON")

        if not isinstance(spec, dict):
            raise RipeAtlasToolsException("Spec should be a JSON object")
        return spec

    def _get_measurement_kwargs(self):
        spec = self._clean_json_spec()

        if self.arguments.type:
            self._type = spec["type"] = self.arguments.type
        else:
            self._type = spec.get("type")
        if not self._type:
            raise RipeAtlasToolsException('Spec should contain a "type"')
        if self._type not in conf["specification"]["types"]:
            raise RipeAtlasToolsException(f"Unknown measurement type: {self._type}")

        from_args = super()._get_measurement_kwargs()

        # Allow override of description or use a different default that doesn't
        # bother about the target
        if not self.arguments.description:
            del from_args["description"]
            if "description" not in spec:
                spec["description"] = f"{self._type.title()} measurement"

        # Allow override of "af" otherwise use the default
        if not self.arguments.af and "af" in spec:
            del from_args["af"]

        spec.update(from_args)

        return spec
