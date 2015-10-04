import unittest
from collections import namedtuple

from ripe.atlas.tools.aggregators.base import aggregate, ValueKeyAggregator, RangeKeyAggregator


class TestAggregators(unittest.TestCase):
    def setUp(self):
        self.results = []
        self.probes = []
        self.Result = namedtuple('Result', 'id probe rtt source prefix')
        self.Probe = namedtuple('Probe', 'id country asn status')
        probes = [
            (1, "GR", 333, "Connected"),
            (2, "NL", 334, "Connected"),
            (3, "SE", 335, "Connected"),
            (4, "SE", 336, "DisConnected"),
            (5, "SE", 337, "DisConnected"),
            (6, "SE", 335, "DisConnected"),
            (7, "IN", 335, "Connected"),
            (8, "DE", 338, "Connected"),
            (9, "DK", 348, "Connected"),
            (10, "DE", 338, "NeverConnected"),
            (11, "DE", 340, "DisConnected"),
        ]
        results = [
            (1, 3, "127.0.0.1", "192/8"),
            (2, 34.0, "127.0.0.1", "192/8"),
            (3, 35.0, "127.0.0.1", "193/8"),
            (4, 6, "127.0.0.1", "193/8"),
            (5, 17, "127.0.0.1", "192/8"),
            (6, 15, "127.0.0.1", "195/8"),
            (7, 35, "127.0.0.1", "192/8"),
            (8, 28, "127.0.0.1", "192/8"),
            (9, 48, "127.0.0.1", "195/8"),
            (10, 28, "127.0.0.1", "194/8"),
            (11, 40, "127.0.0.1", "193/8"),
        ]
        for index, result in enumerate(results):
            prb = self.Probe(
                id=probes[index][0],
                country=probes[index][1],
                asn=probes[index][2],
                status=probes[index][3]
            )
            r = self.Result(
                id=result[0],
                probe=prb,
                rtt=result[1],
                source=result[2],
                prefix=result[3]
            )
            self.results.append(r)
            self.probes.append(prb)

    def test_value_aggregation(self):
        """Test 2 tier aggregation with object attribute as key."""
        keys = [ValueKeyAggregator(key='probe.country'), ValueKeyAggregator(key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'DE': {
                28: [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
                40: [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
            },
             'DK': {48: [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]},
             'GR': {3: [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
             'IN': {35: [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]},
             'NL': {34.0: [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]},
             'SE': {
                6: [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
                15: [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
                17: [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')],
                35.0: [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation1(self):
        """Test 1 tier aggregation"""
        keys = [ValueKeyAggregator(key='probe.country')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'DE': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            'DK': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            'GR': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
            'IN': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            'NL': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
            'SE': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8'), self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation2(self):
        """Test 2 tier aggregation."""
        keys = [ValueKeyAggregator(key='prefix'), ValueKeyAggregator(key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '192/8': {
                3: [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
                17: [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')],
                28: [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')],
                34.0: [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
                35: [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]
            },
            '193/8': {
                6: [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
                35.0: [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')],
                40: [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
            },
            '194/8': {
                28: [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
            },
            '195/8': {
                15: [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
                48: [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation3(self):
        """Test 3 tier aggregation."""
        keys = [ValueKeyAggregator(key='prefix'), ValueKeyAggregator(key='rtt'), ValueKeyAggregator(key='source')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '192/8': {
                3: {
                    '127.0.0.1': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]
                },
                17: {
                    '127.0.0.1': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')]
                },
                28: {
                    '127.0.0.1': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')]
                },
                34.0: {
                    '127.0.0.1': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]
                },
                35: {
                    '127.0.0.1': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]
                }
            },
            '193/8': {
                6: {
                    '127.0.0.1': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
                },
                35.0: {
                    '127.0.0.1': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]
                },
                40: {
                    '127.0.0.1': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
                }
            },
            '194/8': {
                28: {
                    '127.0.0.1': [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
                }
            },
            '195/8': {
                15: {
                    '127.0.0.1': [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
                },
                48: {
                    '127.0.0.1': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
                }
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation4(self):
        """Test 2 tier aggregation with probes."""
        keys = [ValueKeyAggregator(key='status'), ValueKeyAggregator(key='asn')]
        buckets = aggregate(self.probes, keys)
        expected_output = {
            'Connected': {
                338: [self.Probe(id=8, country='DE', asn=338, status='Connected')],
                348: [self.Probe(id=9, country='DK', asn=348, status='Connected')],
                333: [self.Probe(id=1, country='GR', asn=333, status='Connected')],
                334: [self.Probe(id=2, country='NL', asn=334, status='Connected')],
                335: [self.Probe(id=3, country='SE', asn=335, status='Connected'), self.Probe(id=7, country='IN', asn=335, status='Connected')]
            },
            'DisConnected': {
                336: [self.Probe(id=4, country='SE', asn=336, status='DisConnected')],
                337: [self.Probe(id=5, country='SE', asn=337, status='DisConnected')],
                340: [self.Probe(id=11, country='DE', asn=340, status='DisConnected')],
                335: [self.Probe(id=6, country='SE', asn=335, status='DisConnected')]
            },
            'NeverConnected': {
                338: [self.Probe(id=10, country='DE', asn=338, status='NeverConnected')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation(self):
        """Test 1 tier range aggregation"""
        keys = [RangeKeyAggregator(ranges=[10, 20, 30, 40, 50], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            '20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            '30-40': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            '40-50': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            '< 10': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
        }
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation1(self):
        """Test 1 tier range aggregation (1)"""
        keys = [RangeKeyAggregator(ranges=[10, 20, 30, 35, 40, 50, 60], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            '20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            '30-35': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            '35-40': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            '40-50': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            '< 10': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
        }
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation2(self):
        """Test 1 tier range aggregation (2)"""
        keys = [RangeKeyAggregator(ranges=[1, 5, 10, 20, 30, 35], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '1-5': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
            '10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            '20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            '30-35': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            '5-10': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
            '> 35': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]}
        self.assertEquals(buckets, expected_output)

    def test_mixed_aggregation(self):
        """Test value and range aggregation together"""
        keys = [RangeKeyAggregator(ranges=[1, 5, 10, 20, 30, 35], key='rtt'), ValueKeyAggregator(key='probe.country')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '1-5': {
                'GR': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
            '10-20': {
                'SE': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
            },
            '20-30': {
                'DE': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
            },
            '30-35': {
                'IN': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
                'NL': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
                'SE': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]},
            '5-10': {'SE': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]},
            '> 35': {
                'DE': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
                'DK': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_mixed_aggregation1(self):
        """Test value and range aggregation together (1)"""
        keys = [RangeKeyAggregator(ranges=[10, 200], key='rtt'), ValueKeyAggregator(key='probe.country'), ValueKeyAggregator(key='probe.status')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            '10-200': {
                'DE': {
                    'Connected': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')],
                    'DisConnected': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
                    'NeverConnected': [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
                },
                'DK': {'Connected': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]},
                'IN': {'Connected': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]},
                'NL': {'Connected': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]},
                'SE': {
                    'Connected': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')],
                    'DisConnected': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
                }
            },
            '< 10': {
                'GR': {'Connected': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
                'SE': {'DisConnected': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]}
            }
        }
        self.assertEquals(buckets, expected_output)
