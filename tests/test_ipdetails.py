import mock
import unittest
import StringIO

from ripe.atlas.tools.ipdetails import IP


@mock.patch("ripe.atlas.tools.ipdetails.urllib2.urlopen")
@mock.patch("ripe.atlas.tools.ipdetails.cache")
class TestIPDetails(unittest.TestCase):

    RIPESTAT_REQ = {
        'IP': '193.0.6.1',
        'ASN': '3333',
        'SamePrefixIP': '193.0.6.2',
        'SameASDifferentPrefixIP': '193.0.22.1',
        'NotAnnouncedIP': '80.81.192.1',
        'RIPEstatResults': {
          '193.0.6.1': '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:30:00.113317", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.0.0/21)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 561, "query_id": "196d2754-70f6-11e5-b8ba-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": true, "resource": "193.0.0.0/21", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": true, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}',
          '193.0.22.1': '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:32:25.778643", "messages": [["warning", "Given resource is not announced but result has been aligned to first-level less-specific (193.0.22.0/23)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 818, "query_id": "7018b6cc-70f6-11e5-8bf8-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": true, "resource": "193.0.22.0/23", "actual_num_related": 0, "num_filtered_out": 0, "asns": [{"holder": "RIPE-NCC-AS Reseaux IP Europeens Network Coordination Centre (RIPE NCC),NL", "asn": 3333}], "announced": true, "related_prefixes": [], "type": "prefix", "block": {"resource": "193.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}',
          '80.81.192.1': '{"status": "ok", "server_id": "stat-app2", "cached": false, "status_code": 200, "time": "2015-10-12T15:33:58.911309", "messages": [["info", "2 routes were filtered due to low visibility (min peers:3)."]], "version": "1.3", "data_call_status": "supported - connecting to ursa", "see_also": [], "process_time": 462, "query_id": "a7d1daee-70f6-11e5-aaec-782bcb346712", "data": {"query_time": "2015-10-12T08:00:00", "is_less_specific": false, "resource": "80.81.192.1", "actual_num_related": 0, "num_filtered_out": 2, "asns": [], "announced": false, "related_prefixes": [], "type": "prefix", "block": {"resource": "80.0.0.0/8", "name": "IANA IPv4 Address Space Registry", "desc": "RIPE NCC (Status: ALLOCATED)"}}}'
        }
    }

    def mock_setUp(self, mock_cache, mock_urlopen):
        # the poor man's fake cache
        self.db = {}

        def db_get(k):
            return self.db.get(k)
        def db_set(k,v,e):
            self.db[k] = v
        def db_keys():
            return self.db.keys()

        mock_cache.get.side_effect = db_get
        mock_cache.set.side_effect = db_set
        mock_cache.keys.side_effect = db_keys

        # mock_urlopen used to count how many times RIPEStat is queried
        # and to avoid real time RIPEstat queries
        def urlopen(url):
            ip = url.split("?resource=")[1]
            return StringIO.StringIO(self.RIPESTAT_REQ["RIPEstatResults"][ip])

        mock_urlopen.side_effect = urlopen

    def test_loopback4(self, mock_cache, mock_urlopen):
        """IPv4 loopback address"""
        self.mock_setUp(mock_cache, mock_urlopen)
        det = IP("127.0.0.1")
        self.assertEquals(det.asn, None)

    def test_loopback6(self, mock_cache, mock_urlopen):
        """IPv6 loopback address"""
        self.mock_setUp(mock_cache, mock_urlopen)
        det = IP("::1")
        self.assertEquals(det.asn, None)

    def test_nocache(self, mock_cache, mock_urlopen):
        """No cache"""
        self.mock_setUp(mock_cache, mock_urlopen)

        det = IP(TestIPDetails.RIPESTAT_REQ["IP"])

        self.assertEquals(det.asn, TestIPDetails.RIPESTAT_REQ["ASN"])
        self.assertEquals(mock_urlopen.call_count, 1)

    def test_fakecache_sameip(self, mock_cache, mock_urlopen):
        """Fake cache, same IP"""
        self.mock_setUp(mock_cache, mock_urlopen)

        det = IP(TestIPDetails.RIPESTAT_REQ["IP"])
        det = IP(TestIPDetails.RIPESTAT_REQ["IP"])

        self.assertEquals(det.asn, TestIPDetails.RIPESTAT_REQ["ASN"])
        self.assertEquals(mock_urlopen.call_count, 1)

    def test_fakecache_sameprefix(self, mock_cache, mock_urlopen):
        """Fake cache, same prefix"""
        self.mock_setUp(mock_cache, mock_urlopen)

        det1 = IP(TestIPDetails.RIPESTAT_REQ["IP"])
        det2 = IP(TestIPDetails.RIPESTAT_REQ["SamePrefixIP"])

        self.assertEquals(det1.asn, TestIPDetails.RIPESTAT_REQ["ASN"])
        self.assertEquals(det2.asn, det1.asn)
        self.assertEquals(mock_urlopen.call_count, 1)

    def test_fakecache_diffprefix(self, mock_cache, mock_urlopen):
        """Fake cache, same AS, different prefix"""
        self.mock_setUp(mock_cache, mock_urlopen)

        det1 = IP(TestIPDetails.RIPESTAT_REQ["IP"])
        det2 = IP(TestIPDetails.RIPESTAT_REQ["SameASDifferentPrefixIP"])

        self.assertEquals(det1.asn, TestIPDetails.RIPESTAT_REQ["ASN"])
        self.assertEquals(det2.asn, det1.asn)
        self.assertEquals(mock_urlopen.call_count, 2)

    def test_fakecache_notannounced(self, mock_cache, mock_urlopen):
        """Fake cache, IP not announced"""
        self.mock_setUp(mock_cache, mock_urlopen)

        det = IP(TestIPDetails.RIPESTAT_REQ["NotAnnouncedIP"])

        self.assertEquals(det.asn, None)
        self.assertEquals(mock_urlopen.call_count, 1)

        det_again = IP(TestIPDetails.RIPESTAT_REQ["NotAnnouncedIP"])

        # now it should be cached
        self.assertEquals(det.asn, None)
        self.assertEquals(mock_urlopen.call_count, 1)
