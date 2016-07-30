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

import os

import unittest
import requests
import shutil
import tempfile

try:
    from unittest import mock  # Python 3.4+
except ImportError:
    import mock

from ripe.atlas.tools.ipdetails import IP
from ripe.atlas.tools.cache import LocalCache


class FakeCache(LocalCache):


    def __init__(self):
        self.paths = []
        LocalCache.__init__(self)

    def _get_or_create_db_path(self):
        path = os.path.join(tempfile.mkdtemp(), "ripe.atlas.tool.unittest")
        self.paths.append(path)
        return path

    def test_cleanup(self):
        for path in self.paths:
            shutil.rmtree(os.path.dirname(path))


fake_cache = FakeCache()


class FakeResponse(object):
    def __init__(self, json_return={}, ok=True):
        self.json_return = json_return
        self.ok = ok
        self.text = "testing"

    def json(self):
        return self.json_return


class FakeErrorResponse(FakeResponse):
    def json(self):
        raise ValueError("json breaks")


class TestIPDetails(unittest.TestCase):

    IP = '193.0.6.1'
    ASN = '3333'
    HOLDER = 'RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL'
    SAME_PREFIX_IP = '193.0.6.2'
    PREFIX = '193.0.0.0/21'
    SAME_AS_DIFFERENT_PREFIX_IP = '193.0.22.1'
    NOT_ANNOUNCED_IP = '80.81.192.1'
    MOCK_RESULTS = {
        IP: {"status": "ok", "server_id": "stat-app2", "cached": False, "status_code": 200, "time": "2015-10-12T15:30:00.113317", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.0.0/21)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 561, "query_id": "196d2754-70f6-11e5-b8ba-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": True, "resource": "193.0.0.0/21", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": True, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}},
        SAME_AS_DIFFERENT_PREFIX_IP: {"status": "ok", "server_id": "stat-app2", "cached": False, "status_code": 200, "time": "2015-10-12T15:32:25.778643", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.22.0/23)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 818, "query_id": "7018b6cc-70f6-11e5-8bf8-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": True, "resource": "193.0.22.0/23", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": True, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}},
        NOT_ANNOUNCED_IP: {"status": "ok", "server_id": "stat-app2", "cached": False, "status_code": 200, "time": "2015-10-12T15:33:58.911309", "messages": [["info", "2 routes were filtered due to low visibility (min peers:3)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 462, "query_id": "a7d1daee-70f6-11e5-aaec-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": False, "resource": "80.81.192.1", "actual_num_related": 0, "num_filtered_out": 2, "asns": [], "announced": False, "related_prefixes": [], "type": "prefix", "block": {"resource": "80.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}
    }

    def setUp(self):
        fake_cache.clear()

        self.mock_cache = mock.patch(
            "ripe.atlas.tools.ipdetails.cache", wraps=fake_cache
        ).start()
        self.mock_get = mock.patch(
            'ripe.atlas.tools.ipdetails.requests.get'
        ).start()
        self.mock_get.return_value = FakeResponse(
            json_return=self.MOCK_RESULTS[self.IP]
        )

    def tearDown(self):
        mock.patch.stopall()

    @classmethod
    def tearDownClass(cls):
        fake_cache._db.close()
        fake_cache.test_cleanup()

    def test_loopback4(self):
        """IPv4 loopback address"""
        det = IP("127.0.0.1")
        self.assertEquals(det.asn, None)
        self.assertEquals(det.is_querable(), False)
        # no query to stat
        self.assertEquals(self.mock_get.call_count, 0)
        # no access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 0)

    def test_loopback6(self):
        """IPv6 loopback address"""
        det = IP("::1")
        self.assertEquals(det.asn, None)
        self.assertEquals(det.is_querable(), False)
        # no query to stat
        self.assertEquals(self.mock_get.call_count, 0)
        # no access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 0)

    def test_nocache(self):
        """No cache"""
        det = IP(self.IP)

        self.assertEquals(det.asn, self.ASN)
        self.assertEquals(det.prefix, self.PREFIX)
        self.assertEquals(det.holder, self.HOLDER)
        # query to stat
        self.assertEquals(self.mock_get.call_count, 1)
        # access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 1)
        # access to cache set
        self.assertEquals(self.mock_cache.set.call_count, 2)

    def test_fakecache_sameip(self):
        """Fake cache, same IP"""
        det = IP(self.IP)
        det = IP(self.IP)

        self.assertEquals(det.asn, self.ASN)
        # query to stat
        self.assertEquals(self.mock_get.call_count, 1)
        # access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 2)
        # access to cache set
        self.assertEquals(self.mock_cache.set.call_count, 2)

    def test_fakecache_sameprefix(self):
        """Fake cache, same prefix"""
        det1 = IP(self.IP)
        det2 = IP(self.SAME_PREFIX_IP)

        self.assertEquals(det1.asn, self.ASN)
        self.assertEquals(det2.asn, det1.asn)
        # query to stat
        self.assertEquals(self.mock_get.call_count, 1)
        # access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 3)
        # access to cache set
        self.assertEquals(self.mock_cache.set.call_count, 3)

    def test_fakecache_diffprefix(self):
        """Fake cache, same AS, different prefix"""
        self.mock_get.return_value = FakeResponse(
            json_return=self.MOCK_RESULTS[self.IP]
        )
        det1 = IP(self.IP)
        self.mock_get.return_value = FakeResponse(
            json_return=self.MOCK_RESULTS[self.SAME_AS_DIFFERENT_PREFIX_IP]
        )
        det2 = IP(self.SAME_AS_DIFFERENT_PREFIX_IP)

        self.assertEquals(det1.asn, self.ASN)
        self.assertEquals(det2.asn, det1.asn)
        self.assertEquals(self.mock_get.call_count, 2)
        # access to cache get
        self.assertEquals(self.mock_cache.get.call_count, 3)
        # access to cache set
        self.assertEquals(self.mock_cache.set.call_count, 4)

    def test_fakecache_notannounced(self):
        """Fake cache, IP not announced"""
        self.mock_get.return_value = FakeResponse(
            json_return=self.MOCK_RESULTS[self.NOT_ANNOUNCED_IP]
        )
        det = IP(self.NOT_ANNOUNCED_IP)

        self.assertEquals(det.asn, None)
        self.assertEquals(self.mock_get.call_count, 1)

        IP(self.NOT_ANNOUNCED_IP)

        # now it should be cached
        self.assertEquals(det.asn, None)
        self.assertEquals(self.mock_get.call_count, 2)

    def test_valid_query_stat(self):
        """Test case for valid stat response"""
        ip = IP(self.IP)
        self.assertEqual(
            ip.query_stat(),
            {
                'Prefix': '193.0.0.0/21',
                'Holder': 'RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL',
                'ASN': '3333'
            }
        )

    def test_invalid_query_stat(self):
        """Test case where stat returns not ok status"""
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "notok"}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        self.mock_get.return_value = FakeResponse(
            json_return={}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

    def test_invalid_query_stat1(self):
        """Test case where stat returns not valid data structure"""
        # no data at all
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "ok"}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        # data is dict but no asns key
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "ok", "data": {"bla": "bla"}}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        # data is not dict
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "ok", "data": [1, 2]}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        # asns is not list
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "ok", "data": {"asns": {}}}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        # asns is empty
        self.mock_get.return_value = FakeResponse(
            json_return={"status": "ok", "data": {"asns": [{}]}}
        )
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

    def test_invalid_query_stat2(self):
        """Test case where stat returns exception"""
        self.mock_get.side_effect = requests.exceptions.RequestException
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

        self.mock_get.return_value = FakeErrorResponse()
        ip = IP(self.IP)
        self.assertEqual(ip.query_stat(), {})

    def test_update_cache(self):
        """Test case where we store both prefix/address"""
        details = {
            'Prefix': '193.0.0.0/21',
            'Holder': 'RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL',
            'ASN': '3333'
        }
        IP(self.IP)
        self.assertEquals(self.mock_cache.set.call_count, 2)
        self.assertEquals(self.mock_cache.get("IPDetails:193.0.6.1"), details)
        self.assertEquals(self.mock_cache.get(
            "IPDetailsPrefix:193.0.0.0/21"), details
        )

    def test_update_cache1(self):
        """Test case where we store only address"""
        details = {
            'Prefix': '193.0.0.0/21',
            'Holder': 'RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL',
            'ASN': '3333'
        }
        self.mock_cache.set("IPDetailsPrefix:193.0.0.0/21", details, 1)
        IP(self.IP)
        # we already called it above, so it should be 2 by bow
        self.assertEquals(self.mock_cache.set.call_count, 2)
        self.assertEquals(self.mock_cache.get("IPDetails:193.0.6.1"), details)
        self.assertEquals(self.mock_cache.get("IPDetailsPrefix:193.0.0.0/21"), details)

    def test_get_from_cache_prefix(self):
        """Test case where we have a matching prefix in cache"""
        details = {
            'Prefix': '193.0.0.0/21',
            'Holder': 'test',
            'ASN': 'test'
        }
        self.mock_cache.set("IPDetailsPrefix:193.0.0.0/20", details, 1)
        ip = IP(self.IP)
        self.assertTrue(ip.cached_prefix_found)
        self.assertEquals(ip.asn, "test")
        self.assertEquals(ip.holder, "test")
        self.assertEquals(ip.get_from_cached_prefix(), details)

    def test_get_from_cache_prefix1(self):
        """Test case where we dont' have a matching prefix in cache"""
        ip = IP(self.IP)
        # clear out db to test specific function
        self.mock_cache.clear()
        self.assertFalse(ip.cached_prefix_found)
        self.assertEquals(ip.get_from_cached_prefix(), None)

    def test_is_querable(self):
        """Test case where IP is quearable"""
        ip = IP(self.IP)
        self.assertTrue(ip.is_querable())

    def test_is_querable1(self):
        """Test case where IP is not quearable"""
        ip = IP("127.0.0.1")
        self.assertFalse(ip.is_querable())
