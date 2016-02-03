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

from ..helpers.rendering import SaganSet


class ValueKeyAggregator(object):
    """Aggregator based on tha actual value of the key/attribute"""
    def __init__(self, key, prefix=None):
        self.aggregation_keys = key.split('.')
        self.key_prefix = prefix or self.aggregation_keys[-1].upper()

    def get_key_value(self, entity):
        """
        Returns the value of the key/attribute the aggregation will use to
        bucketize probes/results
        """
        attribute = entity
        for key in self.aggregation_keys:
            attribute = getattr(attribute, key)
        return attribute

    def get_bucket(self, entity):
        """
        Returns the bucket the specific entity belongs to based on the give
        key/attribute
        """
        return "{0}: {1}".format(self.key_prefix, self.get_key_value(entity))

    def insert2bucket(self, buckets, bucket, entity):
        if bucket in buckets:
            buckets[bucket].append(entity)
        else:
            buckets[bucket] = [entity]


class RangeKeyAggregator(ValueKeyAggregator):
    """
    Aggregator based on where the position of the value of the key/attribute is
    in the given range
    """

    def __init__(self, key, ranges):
        ValueKeyAggregator.__init__(self, key)
        self.aggregation_ranges = sorted(ranges, reverse=True)

    def get_bucket(self, entity):
        """
        Returns the bucket the specific entity belongs to based on the give
        key/attribute
        """

        bucket = "{0}: < {1}".format(
            self.key_prefix, self.aggregation_ranges[-1])

        key_value = self.get_key_value(entity)
        for index, krange in enumerate(self.aggregation_ranges):
            if key_value > krange:
                if index == 0:
                    bucket = "{0}: > {1}".format(self.key_prefix, krange)
                else:
                    bucket = "{0}: {1}-{2}".format(
                        self.key_prefix,
                        krange,
                        self.aggregation_ranges[index - 1]
                    )
                break

        return bucket


def aggregate(entities, aggregators):
    """
    This is doing the len(aggregators) level aggregation of the entities.
    Caution: being recursive is a bit hard to read/understand, if you change
    something make sure you run tests.
    """

    if not aggregators:
        return entities

    if isinstance(entities, (list, SaganSet)):

        aggregator = aggregators.pop(0)
        buckets = {}
        for entity in entities:
            bucket = aggregator.get_bucket(entity)
            aggregator.insert2bucket(buckets, bucket, entity)
        return aggregate(buckets, aggregators)

    elif isinstance(entities, dict):

        for k, v in entities.items():
            entities[k] = aggregate(entities[k], aggregators[:])

    return entities
