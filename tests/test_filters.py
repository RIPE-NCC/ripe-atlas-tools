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
from ripe.atlas.cousteau import Probe
from ripe.atlas.tools.exceptions import RipeAtlasToolsException
from ripe.atlas.tools.filters import (
    FilterFactory, Filter, ASNFilter, filter_results
)


class TestFilterFactory(unittest.TestCase):
    def test_factory_create(self):
        """Test factory create."""
        self.assertIsInstance(FilterFactory.create("country", "GR"), Filter)
        self.assertIsInstance(FilterFactory.create("asn", "3333"), ASNFilter)


class TestFilter(unittest.TestCase):

    def test_filter(self):
        """Tests filter method of general Filter class."""
        result = {'af': 4, 'prb_id': 1216, 'result': [{'rtt': 27.429}, {'rtt': 25.672}, {'rtt': 25.681}], 'ttl': 54, 'avg': 26.2606666667, 'size': 20, 'from': '109.190.83.40', ' proto': 'ICMP', 'timestamp': 1445025400, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4700, 'max': 27.429, 'step': 360, 'src_addr': '192.168.103.132', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 377, 'dst_name': 'hsi.cablecom.ch', 'min': 25.672, 'dst_addr': '62.2.16.24'}
        sagan_result = Result.get(
            result, on_error=Result.ACTION_IGNORE, on_warning=Result.ACTION_IGNORE
        )
        sagan_result.probe = Probe(
            id=1216,
            meta_data={"country_code": "GR", "asn_v4": 3337, "asn_v6": "4445"}
        )
        self.assertTrue(Filter("country_code", "GR").filter(sagan_result))
        self.assertFalse(Filter("country_code", "NL").filter(sagan_result))
        self.assertFalse(Filter("asn_v4", 3336).filter(sagan_result))
        self.assertTrue(Filter("asn_v6", "4445").filter(sagan_result))

        with self.assertRaises(RipeAtlasToolsException):
            self.assertTrue(Filter("country", "GR").filter(sagan_result))


class TestASNFilter(unittest.TestCase):

    def test_filter(self):
        """Tests filter method of probe's asn filter class."""
        result = {'af': 4, 'prb_id': 1216, 'result': [{'rtt': 27.429}, {'rtt': 25.672}, {'rtt': 25.681}], 'ttl': 54, 'avg': 26.2606666667, 'size': 20, 'from': '109.190.83.40', ' proto': 'ICMP', 'timestamp': 1445025400, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4700, 'max': 27.429, 'step': 360, 'src_addr': '192.168.103.132', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 377, 'dst_name': 'hsi.cablecom.ch', 'min': 25.672, 'dst_addr': '62.2.16.24'}
        sagan_result = Result.get(
            result, on_error=Result.ACTION_IGNORE, on_warning=Result.ACTION_IGNORE
        )
        sagan_result.probe = Probe(
            id=1216,
            meta_data={"country_code": "GR", "asn_v4": 3337, "asn_v6": "4445"}
        )
        self.assertTrue(ASNFilter(3337).filter(sagan_result))
        self.assertFalse(ASNFilter(3336).filter(sagan_result))
        self.assertTrue(ASNFilter("4445").filter(sagan_result))
        self.assertFalse(ASNFilter(4445).filter(sagan_result))


class TestFilterResults(unittest.TestCase):
    def setUp(self):
        result = {'af': 4, 'prb_id': 1216, 'result': [{'rtt': 27.429}, {'rtt': 25.672}, {'rtt': 25.681}], 'ttl': 54, 'avg': 26.2606666667, 'size': 20, 'from': '109.190.83.40', ' proto': 'ICMP', 'timestamp': 1445025400, 'dup': 0, 'type': 'ping', 'sent': 3, 'msm_id': 1000192, 'fw': 4700, 'max': 27.429, 'step': 360, 'src_addr': '192.168.103.132', 'rcvd': 3, 'msm_name': 'Ping', 'lts': 377, 'dst_name': 'hsi.cablecom.ch', 'min': 25.672, 'dst_addr': '62.2.16.24'}

        probes = [
            Probe(
                id=1216,
                meta_data={"country_code": "GR", "asn_v4": 3337, "asn_v6": "4445"}
            ),
            Probe(
                id=121,
                meta_data={"country_code": "GR", "asn_v4": 3338, "asn_v6": "4445"}
            ),
            Probe(
                id=12,
                meta_data={"country_code": "DE", "asn_v4": 3339, "asn_v6": 3337}
            ),
            Probe(
                id=1,
                meta_data={"country_code": "NL", "asn_v4": 3337, "asn_v6": "4446"}
            )
        ]
        self.sagan_results = []
        for probe in probes:
            sagan_result = Result.get(
                result, on_error=Result.ACTION_IGNORE, on_warning=Result.ACTION_IGNORE
            )
            sagan_result.probe = probe
            self.sagan_results.append(sagan_result)

    def test_filter_results1(self):
        """Tests filter results where we have 3 results match with 2 filters."""
        expected_results = [
            self.sagan_results[0], self.sagan_results[2], self.sagan_results[3]
        ]
        filters = [
            FilterFactory.create("asn", 3337),
            FilterFactory.create("country_code", "NL")
        ]
        self.assertEqual(
            filter_results(filters, self.sagan_results), expected_results
        )

    def test_filter_results2(self):
        """Tests filter results where we have no results match with multiple filters."""
        expected_results = []
        filters = [
            FilterFactory.create("asn", 3336),
            FilterFactory.create("country_code", "DK"),
            FilterFactory.create("asn_v6", "3")
        ]
        self.assertEqual(
            filter_results(filters, self.sagan_results), expected_results
        )

    def test_filter_results3(self):
        """Tests filter results where we have success from one of the filters."""
        expected_results = [self.sagan_results[3]]
        filters = [
            FilterFactory.create("asn", 3336),
            FilterFactory.create("country_code", "NL")
        ]
        self.assertEqual(
            filter_results(filters, self.sagan_results), expected_results
        )

    def test_filter_results4(self):
        """Tests filter results where we have success from both of the filters."""
        expected_results = [self.sagan_results[3]]
        filters = [
            FilterFactory.create("asn_v6", "4446"),
            FilterFactory.create("country_code", "NL")
        ]
        self.assertEqual(
            filter_results(filters, self.sagan_results), expected_results
        )
