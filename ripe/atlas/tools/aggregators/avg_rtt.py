import json

from .base import Aggregator as BaseAggregator
from argparse import ArgumentTypeError

class AvgRTTAggregator(BaseAggregator):

  REQUIRES = "rtt_average"
  THRESHOLDS = [10, 20, 30, 40, 50, 100, 200, 300]

  def _prepare(self):
      cust_thresholds = []
      err = "A list of comma-separated integers representing RTT " \
            "thresholds (in ms) must be provided for the \"" \
            "thresholds\" option."

      if self.options:
        for opt in self.options:
            try:
                if opt.split("=")[0] == "thresholds":
                    val = opt.split("=")[1]
                    for t in val.split(","):
                        if not t.isdigit():
                            raise ArgumentTypeError(err)
                        else:
                            cust_thresholds.append(int(t))
            except ArgumentTypeError:
                raise
            except:
                pass

      if cust_thresholds:
        self.THRESHOLDS = sorted(cust_thresholds)

  def _get_aggr_key(self, probe, sagan):
      rtt = sagan.rtt_average
      under = [t for t in self.THRESHOLDS if t <= rtt]
      over = [t for t in self.THRESHOLDS if t > rtt]
      if over:
          if under:
            return "{}-{} ms".format(under[-1],over[0])
          else:
            return "< {} ms".format(over[0])
      else:
          return "> {} ms".format(self.THRESHOLDS[-1])
