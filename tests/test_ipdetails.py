import mock
import unittest
try:
    from cStringIO import StringIO
except:
    # python 3
    from io import StringIO

from ripe.atlas.tools.ipdetails import IP


class TestIPDetails(unittest.TestCase):

    IP = '193.0.6.1'
    ASN = '3333'
    HOLDER = 'RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL'
    SAME_PREFIX_IP = '193.0.6.2'
    SAME_AS_DIFFERENT_PREFIX_IP = '193.0.22.1'
    NOT_ANNOUNCED_IP = '80.81.192.1'
    MOCK_RESULTS = {
        IP: '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:30:00.113317", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.0.0/21)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 561, "query_id": "196d2754-70f6-11e5-b8ba-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": true, "resource": "193.0.0.0/21", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": true, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}',
        SAME_AS_DIFFERENT_PREFIX_IP: '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:32:25.778643", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.22.0/23)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 818, "query_id": "7018b6cc-70f6-11e5-8bf8-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": true, "resource": "193.0.22.0/23", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": true, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}',
        NOT_ANNOUNCED_IP: '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:33:58.911309", "messages": [["info", "2 routes were filtered due to low visibility (min peers:3)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 462, "query_id": "a7d1daee-70f6-11e5-aaec-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": false, "resource": "80.81.192.1", "actual_num_related": 0, "num_filtered_out": 2, "asns": [], "announced": false, "related_prefixes": [], "type": "prefix", "block": {"resource": "80.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}'
    }

    def setUp(self):
        # the poor man's fake cache
        self.db = {}

        def db_get(k):
            return self.db.get(k)
        def db_set(k,v,e):
            self.db[k] = v
        def db_keys():
            return self.db.keys()

        self.mock_cache_patcher = \
            mock.patch("ripe.atlas.tools.ipdetails.cache")
        self.mock_cache = self.mock_cache_patcher.start()
        self.mock_cache.get.side_effect = db_get
        self.mock_cache.set.side_effect = db_set
        self.mock_cache.keys.side_effect = db_keys

        # mock_urlopen used to count how many times RIPEStat is queried
        # and to avoid real time RIPEstat queries
        def urlopen(url):
            ip = url.split("?resource=")[1]
            return StringIO(self.MOCK_RESULTS[ip])

        self.mock_urlopen_patcher = \
            mock.patch("ripe.atlas.tools.ipdetails.urllib2.urlopen")
        self.mock_urlopen = self.mock_urlopen_patcher.start()
        self.mock_urlopen.side_effect = urlopen

    def tearDown(self):
        self.mock_cache_patcher.stop()
        self.mock_urlopen_patcher.stop()

    def test_loopback4(self):
        """IPv4 loopback address"""
        det = IP("127.0.0.1")
        self.assertEquals(det.asn, None)

    def test_loopback6(self):
        """IPv6 loopback address"""
        det = IP("::1")
        self.assertEquals(det.asn, None)

    def test_nocache(self):
        """No cache"""
        det = IP(self.IP)

        self.assertEquals(det.asn, self.ASN)
        self.assertEquals(det.holder, self.HOLDER)
        self.assertEquals(self.mock_urlopen.call_count, 1)

    def test_fakecache_sameip(self):
        """Fake cache, same IP"""
        det = IP(self.IP)
        det = IP(self.IP)

        self.assertEquals(det.asn, self.ASN)
        self.assertEquals(self.mock_urlopen.call_count, 1)

    def test_fakecache_sameprefix(self):
        """Fake cache, same prefix"""
        det1 = IP(self.IP)
        det2 = IP(self.SAME_PREFIX_IP)

        self.assertEquals(det1.asn, self.ASN)
        self.assertEquals(det2.asn, det1.asn)
        self.assertEquals(self.mock_urlopen.call_count, 1)

    def test_fakecache_diffprefix(self):
        """Fake cache, same AS, different prefix"""
        det1 = IP(self.IP)
        det2 = IP(self.SAME_AS_DIFFERENT_PREFIX_IP)

        self.assertEquals(det1.asn, self.ASN)
        self.assertEquals(det2.asn, det1.asn)
        self.assertEquals(self.mock_urlopen.call_count, 2)

    def test_fakecache_notannounced(self):
        """Fake cache, IP not announced"""
        det = IP(self.NOT_ANNOUNCED_IP)

        self.assertEquals(det.asn, None)
        self.assertEquals(self.mock_urlopen.call_count, 1)

        det_again = IP(self.NOT_ANNOUNCED_IP)

        # now it should be cached
        self.assertEquals(det.asn, None)
        self.assertEquals(self.mock_urlopen.call_count, 1)
