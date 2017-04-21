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

from tzlocal import get_localzone
from datetime import datetime
from .base import Renderer as BaseRenderer
from ..helpers.colours import colourise


class Renderer(BaseRenderer):
    RENDERS = [BaseRenderer.TYPE_NTP]

    def on_result(self, result):
        created = result.created.astimezone(get_localzone())
        probe_id = result.probe_id
        r = '\n\nProbe #{0}\n{1}\n'.format(probe_id, '=' * 79)
        res = self.get_formatted_response(probe_id, created, result)
        if res:
            return r + res
        else:
            return colourise(r + 'No results\n', 'red')

    def get_formatted_response(self, probe_id, created, result):
        leap = result.leap_second_indicator
        stratum = result.stratum
        v = result.version
        mode = result.mode
        # just here for completeness, flake8 doesn't like when it's not used
        # end_time = result.end_time
        poll = result.poll
        precision = result.precision
        refid = result.reference_id
        ref_time = result.reference_time
        root_delay = result.root_delay
        root_disp = result.root_dispersion

        if not leap and not stratum and not v and not mode:
            return

        if mode != 'server':
            print('invalid mode: %s' % mode)

        r = '[NTP] %s -> %s (%s)\n' % (result.source_address,
                                       result.destination_name,
                                       result.destination_address)
        r += '\tversion: %s, stratum: %s/16\n' % (colourise(v, 'bold'),
                                                  colourise(stratum, 'bold'))
        r += '\trefid: %s\n' % colourise(refid, 'bold')
        r += '\tleap: %s, poll: %s, precision: %s\n' % (leap, poll, precision)
        r += '\troot_delay: %s, root_disp: %s\n' % (root_delay, root_disp)
        r += '\tref-time: %s\n\n' % datetime.fromtimestamp(ref_time)

        try:
            for idx, pkt in enumerate(result.packets):
                r += '\t[%s] %s\n' % (idx, str(pkt))
                r += '\t\ttrans: %s -> recv: %s\n' % (pkt.transmitted_time,
                                                      pkt.received_time)
                r += '\t\torigin: %s -> final: %s\n\n' % (pkt.origin_time,
                                                          pkt.final_time)
        except Exception as ex:
            print('Got exception when reading packet: %s' % ex)
            print('Raw: %s' % pkt.raw_data)

        return r
