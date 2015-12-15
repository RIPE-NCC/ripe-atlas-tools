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
from collections import namedtuple

from ripe.atlas.tools.aggregators.base import (
    aggregate, ValueKeyAggregator, RangeKeyAggregator
)


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
            'COUNTRY: DE': {
                'RTT: 28': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
                'RTT: 40': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
            },
            'COUNTRY: DK': {'RTT: 48': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]},
            'COUNTRY: GR': {'RTT: 3': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
            'COUNTRY: IN': {'RTT: 35': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]},
            'COUNTRY: NL': {'RTT: 34.0': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]},
            'COUNTRY: SE': {
                'RTT: 6': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
                'RTT: 15': [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
                'RTT: 17': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')],
                'RTT: 35.0': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation1(self):
        """Test 1 tier aggregation"""
        keys = [ValueKeyAggregator(key='probe.country')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'COUNTRY: DE': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            'COUNTRY: DK': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            'COUNTRY: GR': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
            'COUNTRY: IN': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            'COUNTRY: NL': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
            'COUNTRY: SE': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8'), self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation2(self):
        """Test 2 tier aggregation."""
        keys = [ValueKeyAggregator(key='prefix'), ValueKeyAggregator(key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'PREFIX: 192/8': {
                'RTT: 3': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
                'RTT: 17': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')],
                'RTT: 28': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')],
                'RTT: 34.0': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
                'RTT: 35': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]
            },
            'PREFIX: 193/8': {
                'RTT: 6': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
                'RTT: 35.0': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')],
                'RTT: 40': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
            },
            'PREFIX: 194/8': {
                'RTT: 28': [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
            },
            'PREFIX: 195/8': {
                'RTT: 15': [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
                'RTT: 48': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation3(self):
        """Test 3 tier aggregation."""
        keys = [ValueKeyAggregator(key='prefix'), ValueKeyAggregator(key='rtt'), ValueKeyAggregator(key='source')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'PREFIX: 192/8': {
                'RTT: 3': {
                    'SOURCE: 127.0.0.1': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]
                },
                'RTT: 17': {
                    'SOURCE: 127.0.0.1': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8')]
                },
                'RTT: 28': {
                    'SOURCE: 127.0.0.1': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')]
                },
                'RTT: 34.0': {
                    'SOURCE: 127.0.0.1': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]
                },
                'RTT: 35': {
                    'SOURCE: 127.0.0.1': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]
                }
            },
            'PREFIX: 193/8': {
                'RTT: 6': {
                    'SOURCE: 127.0.0.1': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
                },
                'RTT: 35.0': {
                    'SOURCE: 127.0.0.1': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]
                },
                'RTT: 40': {
                    'SOURCE: 127.0.0.1': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]
                }
            },
            'PREFIX: 194/8': {
                'RTT: 28': {
                    'SOURCE: 127.0.0.1': [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
                }
            },
            'PREFIX: 195/8': {
                'RTT: 15': {
                    'SOURCE: 127.0.0.1': [self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
                },
                'RTT: 48': {
                    'SOURCE: 127.0.0.1': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
                }
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_value_aggregation4(self):
        """Test 2 tier aggregation with probes."""
        keys = [ValueKeyAggregator(key='status'), ValueKeyAggregator(key='asn')]
        buckets = aggregate(self.probes, keys)
        expected_output = {
            'STATUS: Connected': {
                'ASN: 338': [self.Probe(id=8, country='DE', asn=338, status='Connected')],
                'ASN: 348': [self.Probe(id=9, country='DK', asn=348, status='Connected')],
                'ASN: 333': [self.Probe(id=1, country='GR', asn=333, status='Connected')],
                'ASN: 334': [self.Probe(id=2, country='NL', asn=334, status='Connected')],
                'ASN: 335': [self.Probe(id=3, country='SE', asn=335, status='Connected'), self.Probe(id=7, country='IN', asn=335, status='Connected')]
            },
            'STATUS: DisConnected': {
                'ASN: 336': [self.Probe(id=4, country='SE', asn=336, status='DisConnected')],
                'ASN: 337': [self.Probe(id=5, country='SE', asn=337, status='DisConnected')],
                'ASN: 340': [self.Probe(id=11, country='DE', asn=340, status='DisConnected')],
                'ASN: 335': [self.Probe(id=6, country='SE', asn=335, status='DisConnected')]
            },
            'STATUS: NeverConnected': {
                'ASN: 338': [self.Probe(id=10, country='DE', asn=338, status='NeverConnected')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation(self):
        """Test 1 tier range aggregation"""
        keys = [RangeKeyAggregator(ranges=[10, 20, 30, 40, 50], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'RTT: 10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            'RTT: 20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            'RTT: 30-40': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            'RTT: 40-50': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            'RTT: < 10': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
        }
        self.maxDiff = None
        import pprint
        pp = pprint.PrettyPrinter()
        pp.pprint(buckets)
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation1(self):
        """Test 1 tier range aggregation (1)"""
        keys = [RangeKeyAggregator(ranges=[10, 20, 30, 35, 40, 50, 60], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'RTT: 10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            'RTT: 20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            'RTT: 30-35': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            'RTT: 35-40': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
            'RTT: 40-50': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')],
            'RTT: < 10': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8'), self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]
        }
        self.assertEquals(buckets, expected_output)

    def test_range_aggregation2(self):
        """Test 1 tier range aggregation (2)"""
        keys = [RangeKeyAggregator(ranges=[1, 5, 10, 20, 30, 35], key='rtt')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'RTT: 1-5': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')],
            'RTT: 10-20': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')],
            'RTT: 20-30': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')],
            'RTT: 30-35': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8'), self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8'), self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
            'RTT: 5-10': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')],
            'RTT: > 35': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8'), self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')]}
        self.assertEquals(buckets, expected_output)

    def test_mixed_aggregation(self):
        """Test value and range aggregation together"""
        keys = [RangeKeyAggregator(ranges=[1, 5, 10, 20, 30, 35], key='rtt'), ValueKeyAggregator(key='probe.country')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'RTT: 1-5': {
                'COUNTRY: GR': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
            'RTT: 10-20': {
                'COUNTRY: SE': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
            },
            'RTT: 20-30': {
                'COUNTRY: DE': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8'), self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
            },
            'RTT: 30-35': {
                'COUNTRY: IN': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')],
                'COUNTRY: NL': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')],
                'COUNTRY: SE': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')]},
            'RTT: 5-10': {'COUNTRY: SE': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]},
            'RTT: > 35': {
                'COUNTRY: DE': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
                'COUNTRY: DK': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]
            }
        }
        self.assertEquals(buckets, expected_output)

    def test_mixed_aggregation1(self):
        """Test value and range aggregation together (1)"""
        keys = [RangeKeyAggregator(ranges=[10, 200], key='rtt'), ValueKeyAggregator(key='probe.country'), ValueKeyAggregator(key='probe.status')]
        buckets = aggregate(self.results, keys)
        expected_output = {
            'RTT: 10-200': {
                'COUNTRY: DE': {
                    'STATUS: Connected': [self.Result(id=8, probe=self.Probe(id=8, country='DE', asn=338, status='Connected'), rtt=28, source='127.0.0.1', prefix='192/8')],
                    'STATUS: DisConnected': [self.Result(id=11, probe=self.Probe(id=11, country='DE', asn=340, status='DisConnected'), rtt=40, source='127.0.0.1', prefix='193/8')],
                    'STATUS: NeverConnected': [self.Result(id=10, probe=self.Probe(id=10, country='DE', asn=338, status='NeverConnected'), rtt=28, source='127.0.0.1', prefix='194/8')]
                },
                'COUNTRY: DK': {'STATUS: Connected': [self.Result(id=9, probe=self.Probe(id=9, country='DK', asn=348, status='Connected'), rtt=48, source='127.0.0.1', prefix='195/8')]},
                'COUNTRY: IN': {'STATUS: Connected': [self.Result(id=7, probe=self.Probe(id=7, country='IN', asn=335, status='Connected'), rtt=35, source='127.0.0.1', prefix='192/8')]},
                'COUNTRY: NL': {'STATUS: Connected': [self.Result(id=2, probe=self.Probe(id=2, country='NL', asn=334, status='Connected'), rtt=34.0, source='127.0.0.1', prefix='192/8')]},
                'COUNTRY: SE': {
                    'STATUS: Connected': [self.Result(id=3, probe=self.Probe(id=3, country='SE', asn=335, status='Connected'), rtt=35.0, source='127.0.0.1', prefix='193/8')],
                    'STATUS: DisConnected': [self.Result(id=5, probe=self.Probe(id=5, country='SE', asn=337, status='DisConnected'), rtt=17, source='127.0.0.1', prefix='192/8'), self.Result(id=6, probe=self.Probe(id=6, country='SE', asn=335, status='DisConnected'), rtt=15, source='127.0.0.1', prefix='195/8')]
                }
            },
            'RTT: < 10': {
                'COUNTRY: GR': {'STATUS: Connected': [self.Result(id=1, probe=self.Probe(id=1, country='GR', asn=333, status='Connected'), rtt=3, source='127.0.0.1', prefix='192/8')]},
                'COUNTRY: SE': {'STATUS: DisConnected': [self.Result(id=4, probe=self.Probe(id=4, country='SE', asn=336, status='DisConnected'), rtt=6, source='127.0.0.1', prefix='193/8')]}
            }
        }
        self.assertEquals(buckets, expected_output)
