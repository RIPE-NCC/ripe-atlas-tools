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
import itertools


class ValueKeyAggregator(object):
    """Aggregator based on tha actual value of the key/attribute"""

    def __init__(self, key, prefix=None):
        self.aggregation_keys = key.split(".")
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
            self.key_prefix, self.aggregation_ranges[-1]
        )

        key_value = self.get_key_value(entity)
        for index, krange in enumerate(self.aggregation_ranges):
            if key_value > krange:
                if index == 0:
                    bucket = "{0}: > {1}".format(self.key_prefix, krange)
                else:
                    bucket = "{0}: {1}-{2}".format(
                        self.key_prefix,
                        krange,
                        self.aggregation_ranges[index - 1],
                    )
                break

        return bucket


def _get_sort_key(kv):
    key = []
    for is_digit, part in itertools.groupby(kv[0], key=str.isdigit):
        part = "".join(part)
        if is_digit:
            part = int(part)
        key.append(part)
    return key


def aggregate(entities, aggregators):
    """
    Aggregate the given entities using the given aggregators.

    Returns a dict of {combined_aggregation_key_tuple: entity_list}, where
    the keys are in ascending numeric >> lexical order.
    """
    if not aggregators:
        return entities

    buckets = {}

    for e in entities:
        key = " | ".join(a.get_bucket(e) for a in aggregators)
        bucket = buckets.setdefault(key, [])
        bucket.append(e)

    return dict(sorted(buckets.items(), key=_get_sort_key))
