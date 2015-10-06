import mock
import unittest
from urllib2 import urlopen

from ripe.atlas.tools.ipdetails import IP


@mock.patch("ripe.atlas.tools.ipdetails.urllib2.urlopen")
@mock.patch("ripe.atlas.tools.ipdetails.cache")
class TestIPDetails(unittest.TestCase):

    RIPESTAT_REQ = {
        'IP': '193.0.6.1',
        'ASN': '3333',
        'SamePrefixIP': '193.0.6.2',
        'SameASDifferentPrefixIP': '193.0.22.1',
        'NotAnnouncedIP': '80.81.192.1'
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

        # mock_urlopen just used to count how many times RIPEStat is queried
        mock_urlopen.side_effect = lambda url: urlopen(url)

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
