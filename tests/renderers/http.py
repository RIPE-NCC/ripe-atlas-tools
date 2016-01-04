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

import unittest

from ripe.atlas.sagan import Result
from ripe.atlas.tools.renderers.http import Renderer


class TestHttpRenderer(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.basic = Result.get('{"lts":64,"from":"217.13.64.36","msm_id":2841267,"fw":4720,"timestamp":1450185727,"uri":"http://at-vie-as1120.anchors.atlas.ripe.net:80/4096","prb_id":1,"result":[{"rt":45.953289,"src_addr":"217.13.64.36","hsize":131,"af":4,"bsize":1668618,"res":200,"method":"GET","ver":"1.1","dst_addr":"193.171.255.2"}],"group_id":2841267,"type":"http","msm_name":"HTTPGet"}')
        self.multiple = Result.get('{"lts":64,"from":"217.13.64.36","msm_id":2841267,"fw":4720,"timestamp":1450185727,"uri":"http://at-vie-as1120.anchors.atlas.ripe.net:80/4096","prb_id":1,"result":[{"rt":45.953289,"src_addr":"217.13.64.36","hsize":131,"af":4,"bsize":1668618,"res":200,"method":"GET","ver":"1.1","dst_addr":"193.171.255.2"},{"rt":45.953289,"src_addr":"217.13.64.36","hsize":131,"af":4,"bsize":1668618,"res":200,"method":"GET","ver":"1.1","dst_addr":"193.171.255.2"}],"group_id":2841267,"type":"http","msm_name":"HTTPGet"}')

    def test_basic(self):
        expected = (
            '#Version: 1.0\n'
            '#Date: 2015-12-15 13:22:07\n'
            '#Fields: cs-method cs-uri c-ip s-ip sc-status time-taken http-version header-bytes body-bytes\n'
            'GET http://at-vie-as1120.anchors.atlas.ripe.net:80/4096 217.13.64.36 193.171.255.2 200 45.953289 1.1 131 1668618\n\n'
        )
        self.assertEqual(Renderer().on_result(self.basic), expected)

    def test_multiple(self):
        expected = (
            '#Version: 1.0\n'
            '#Date: 2015-12-15 13:22:07\n'
            '#Fields: cs-method cs-uri c-ip s-ip sc-status time-taken http-version header-bytes body-bytes\n'
            'GET http://at-vie-as1120.anchors.atlas.ripe.net:80/4096 217.13.64.36 193.171.255.2 200 45.953289 1.1 131 1668618\n'
            'GET http://at-vie-as1120.anchors.atlas.ripe.net:80/4096 217.13.64.36 193.171.255.2 200 45.953289 1.1 131 1668618\n\n'
        )
        self.assertEqual(Renderer().on_result(self.multiple), expected)
