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

from .base import Renderer as BaseRenderer
from collections import Counter

from ..helpers.sanitisers import sanitise
from ..ipdetails import IP


class Renderer(BaseRenderer):

    RENDERS = [BaseRenderer.TYPE_PING]

    SHOW_DEFAULT_HEADER = False
    SHOW_DEFAULT_FOOTER = False

    def __init__(self, *args, **kwargs):

        BaseRenderer.__init__(self, *args, **kwargs)

        # Keys are timestamps, data struct captures ASN membership
        self.asns = Counter()
        self.asn2name = {}

    def on_result(self, result):
        dst = result.destination_address
        if dst is not None:
            ip = IP(dst)
            if ip.asn:
                self.asns[ip.asn] += 1
                self.asn2name[ip.asn] = sanitise(ip.holder)
            else:
                self.asns["<unknown>"] += 1
                self.asn2name["<unknown>"] = "unknown"
            return ""
        return ""

    def additional(self):

        total = sum(self.asns.values())

        r = ""
        for asn, count in self.asns.most_common():
            r += "AS%s %.2f%% (%s)" % (
                asn,
                100.0 * count / total,
                self.asn2name[asn],
            )

        return r
