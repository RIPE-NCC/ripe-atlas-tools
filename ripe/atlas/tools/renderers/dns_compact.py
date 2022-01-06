# Copyright (c) 2017 RIPE NCC
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

from tzlocal import get_localzone

from ..helpers.colours import colourise
from ..helpers.sanitisers import sanitise
from .base import Renderer as BaseRenderer


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_DNS]
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    ANSWER_COLORS = ["cyan", "blue"]

    def on_result(self, result):

        created = result.created.astimezone(get_localzone())
        probe_id = result.probe_id

        r = []
        if result.responses:
            for response in result.responses:
                r.append(self.get_formatted_response(probe_id, created, response))
        else:
            r.append(
                "{}{}\n".format(
                    self.get_header(probe_id, created),
                    colourise("No response found", "red"),
                )
            )

        return "".join(r)

    @classmethod
    def get_header(cls, probe_id, created):
        return "Probe {0:>6}: {1} ".format(
            "#{}".format(probe_id),
            created.strftime(cls.TIME_FORMAT),
        )

    @classmethod
    def get_formatted_response(cls, probe_id, created, response):

        s = []
        answers = ""
        if response.abuf:
            header_flags = []
            for flag in (
                "aa",
                "ad",
                "cd",
                "qr",
                "ra",
                "rd",
            ):
                if getattr(response.abuf.header, flag):
                    header_flags.append(flag)
            s.append(response.abuf.header.return_code)
            s.append(" ".join(header_flags))
            answers = cls.print_answers(response.abuf.answers)
        else:
            s.append("No abuf found")

        if response.is_error or not response.abuf:
            color = "red"
        elif len(response.abuf.answers) == 0:
            color = "yellow"
        else:
            color = "green"

        status = colourise(" ".join(s), color)
        return "".join(
            [
                cls.get_header(probe_id, created),
                status,
                " " if answers else "",
                answers,
                "\n",
            ]
        )

    @staticmethod
    def get_rrdata(data):
        """
        Return RRdata in condensed text form.
        """
        if not data:
            return ""
        # It's too complicated to override __str__ method of all Answer
        # classes of Sagan so let's compress it text-wise instead
        r = str(data).split()
        r.pop(2)  # get rid of the class
        return sanitise(" ".join(r))

    @classmethod
    def print_answers(cls, data):
        """
        Return list of colourised condensed textual RRdata.
        """
        r = []
        for record, color in zip(data, cls.ANSWER_COLORS * len(data)):
            r.append(colourise(cls.get_rrdata(record), color))
        return "; ".join(r)
