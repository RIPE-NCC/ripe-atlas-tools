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

import unittest

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

from pytz import timezone
from ripe.atlas.sagan import Result
from ripe.atlas.tools.renderers.dns_compact import Renderer

def get_fake_localzone():
    return timezone('UTC')

@mock.patch('ripe.atlas.tools.renderers.dns_compact.get_localzone', get_fake_localzone)
class TestDnsCompact(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.basic = Result.get('{"lts":92,"from":"195.113.83.16","msm_id":9211416,"fw":4790,"timestamp":1503927916,"resultset":[{"lts":92,"src_addr":"195.113.83.16","af":4,"submax":3,"proto":"UDP","subid":1,"result":{"abuf":"fViBgAABAAIAAgAEBTF4YmV0A2NvbQAAAQABwAwAAQABAAAAGQAEvmnCOsAMAAEAAQAAABkABL550oXADAACAAEAAVUJABUEZGFuYQJucwpjbG91ZGZsYXJlwBLADAACAAEAAVUJAAcEcGV0ZcBMwEcAAQABAAFVCQAErfU6acBHABwAAQABVQkAECQAywAgSQABAAAAAK31OmnAaAABAAEAAVUJAASt9TuIwGgAHAABAAFVCQAQJADLACBJAAEAAAAArfU7iA==","rt":6.45,"NSCOUNT":2,"QDCOUNT":1,"ANCOUNT":2,"ARCOUNT":4,"ID":32088,"size":199},"time":1503927916,"dst_addr":"195.113.83.55"},{"lts":93,"src_addr":"195.113.83.16","af":4,"submax":3,"proto":"UDP","subid":2,"result":{"abuf":"D/uBBQABAAAAAAAABTF4YmV0A2NvbQAAAQAB","rt":5.798,"NSCOUNT":0,"QDCOUNT":1,"ANCOUNT":0,"ARCOUNT":0,"ID":4091,"size":27},"time":1503927917,"dst_addr":"147.231.12.1"},{"lts":94,"src_addr":"2001:718:1e06::16","af":6,"submax":3,"proto":"UDP","subid":3,"result":{"abuf":"pqqBgAABAAIAAgAEBTF4YmV0A2NvbQAAAQABwAwAAQABAAAAFwAEvnnShcAMAAEAAQAAABcABL5pwjrADAACAAEAAVUHABUEcGV0ZQJucwpjbG91ZGZsYXJlwBLADAACAAEAAVUHAAcEZGFuYcBMwGgAAQABAAFVBwAErfU6acBoABwAAQABVQcAECQAywAgSQABAAAAAK31OmnARwABAAEAAVUHAASt9TuIwEcAHAABAAFVBwAQJADLACBJAAEAAAAArfU7iA==","rt":5.684,"NSCOUNT":2,"QDCOUNT":1,"ANCOUNT":2,"ARCOUNT":4,"ID":42666,"size":199},"time":1503927918,"dst_addr":"2001:718:1e06::55"}],"prb_id":4062,"group_id":9211416,"type":"dns","msm_name":"Tdig"}')
        self.noerrornodata = Result.get('{"lts":42,"from":"2001:718:1:a100::161:50","msm_id":9386425,"fw":4780,"proto":"UDP","af":6,"msm_name":"Tdig","prb_id":6068,"result":{"abuf":"8RCAgAABAAAAAQAACGlwdjRvbmx5BGFycGEAABwAAcAMAAYAAQAABikALQNzbnMDZG5zBWljYW5uA29yZwADbm9jwC94Ob7xAAAcIAAADhAACTqAAAAOEA==","rt":153.425,"NSCOUNT":1,"QDCOUNT":1,"ID":61712,"ARCOUNT":0,"ANCOUNT":0,"size":88},"timestamp":1506557387,"src_addr":"2001:718:1:a100::161:50","group_id":9386425,"type":"dns","dst_addr":"2001:4860:4860::6464"}')
        self.noresponse = Result.get('{"lts":11,"from":"2a01:538:1:f000:fa1a:67ff:fe4d:7f1d","msm_id":9386425,"fw":4780,"timestamp":1506681497,"proto":"UDP","msm_name":"Tdig","prb_id":11879,"af":6,"error":{"timeout":5000},"src_addr":"2a01:538:1:f000:fa1a:67ff:fe4d:7f1d","group_id":9386425,"type":"dns","dst_addr":"2001:4860:4860::6464"}')
        self.noabuf = Result.get('{"lts":27,"from":"80.92.240.37","msm_id":9211416,"fw":4780,"timestamp":1503927938,"resultset":[{"lts":27,"src_addr":"192.168.254.254","af":4,"submax":2,"proto":"UDP","subid":1,"time":1503927938,"error":{"timeout":5000},"dst_addr":"80.92.240.6"}],"prb_id":30410,"group_id":9211416,"type":"dns","msm_name":"Tdig"}')

    def test_basic(self):
        self.assertEqual(
            Renderer().on_result(self.basic),
            "Probe  #4062: 2017-08-28 13:45:16 NOERROR qr ra rd 1xbet.com. 25 A 190.105.194.58; 1xbet.com. 25 A 190.121.210.133\n"
            "Probe  #4062: 2017-08-28 13:45:16 REFUSED qr rd\n"
            "Probe  #4062: 2017-08-28 13:45:16 NOERROR qr ra rd 1xbet.com. 23 A 190.121.210.133; 1xbet.com. 23 A 190.105.194.58\n"

        )

    def test_noerrornodata(self):
        self.assertEqual(
            Renderer().on_result(self.noerrornodata),
            "Probe  #6068: 2017-09-28 00:09:47 NOERROR qr ra\n"
        )

    def test_noresponse(self):
        self.assertEqual(
            Renderer().on_result(self.noresponse),
            "Probe #11879: 2017-09-29 10:38:17 No response found\n"
        )

    def test_noabuf(self):
        self.assertEqual(
            Renderer().on_result(self.noabuf),
            "Probe #30410: 2017-08-28 13:45:38 No abuf found\n"
        )
