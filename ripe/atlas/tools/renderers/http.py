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

from ..helpers.colours import colourise

from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):
    """
    We're abusing the Extended Log File Format here to render the result,
    amending it to include a few things not originally specified in the W3C
    Working Draft: http://www.w3.org/TR/WD-logfile.html Namely:
      http-version, header-bytes, and body-bytes
    """

    RENDERS = [BaseRenderer.TYPE_HTTP]
    COLOURS = {
        "2": "green",
        "3": "blue",
        "4": "yellow",
        "5": "red"
    }

    def on_result(self, result, probes=None):
        r = "#Version: 1.0\n#Date: {}\n#Fields: {}\n".format(
            result.created.strftime("%Y-%m-%d %H:%M:%S"),
            "cs-method cs-uri c-ip s-ip sc-status time-taken http-version "
            "header-bytes body-bytes"
        )
        for response in result.responses:
            r += self._colourise_by_status(
                "{} {} {} {} {} {} {} {} {}\n".format(
                    result.method,
                    result.uri,
                    response.source_address,
                    response.destination_address,
                    response.code,
                    response.response_time,
                    response.version,
                    response.head_size,
                    response.body_size
                ),
                response.code
            )

        return r + "\n"

    def _colourise_by_status(self, output, status):
        try:
            return colourise(output, self.COLOURS[str(status)[0]])
        except (IndexError, KeyError):
            return colourise(output, "red")
