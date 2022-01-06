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

import json

from .base import Renderer as BaseRenderer
from ..helpers.sanitisers import sanitise


class Renderer(BaseRenderer):

    RENDERS = [
        BaseRenderer.TYPE_PING,
        BaseRenderer.TYPE_TRACEROUTE,
        BaseRenderer.TYPE_DNS,
        BaseRenderer.TYPE_SSLCERT,
        BaseRenderer.TYPE_HTTP,
        BaseRenderer.TYPE_NTP,
    ]

    SHOW_DEFAULT_HEADER = False
    SHOW_DEFAULT_FOOTER = False

    def on_result(self, result, probes=None):
        return sanitise(json.dumps(result.raw_data, separators=(",", ":"))) + "\n"
