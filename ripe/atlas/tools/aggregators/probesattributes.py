import json

from ripe.atlas.sagan import Result, ResultError

from .base import Aggregator as BaseAggregator


class CountryAggregator(BaseAggregator):

  def _get_aggr_key(self, probe, sagan):
      return probe.country_code


class ASN4Aggregator(BaseAggregator):

  def _get_aggr_key(self, probe, sagan):
      return probe.asn_v4


class ASN6Aggregator(BaseAggregator):

  def _get_aggr_key(self, probe, sagan):
      return probe.asn_v6
